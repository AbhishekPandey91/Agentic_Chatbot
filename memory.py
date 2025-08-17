import asyncio #running multiple tasks "at the same time" without blocking)
import json #saving chatbot responses in JSON format
import time #Provides time-related functions (delays, timestamps, performance checks)
import re #Regular expressions for pattern matching in strings
from datetime import datetime, timedelta 
from typing import Dict, List, Any, TypedDict, Optional
from dataclasses import dataclass, asdict #@dataclass: A decorator that automatically generates class boilerplate code (like __init__, __repr__). &asdict: Converts a dataclass into a dictionary
import streamlit as st
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate #ChatPromptTemplate: A template for creating chat prompts with placeholders for dynamic content
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END #StateGraph: A class for creating state machines or workflows with nodes and edges
from dotenv import load_dotenv #load_dotenv: Loads environment variables from a .env file into the environment
load_dotenv() # Load environment variables from a .env file

@dataclass
class TaskNode:
    id: str
    agent_name: str
    task_description: str
    dependencies: List[str]
    status: str = "pending"  # pending, running, completed, failed
    result: str = ""
    start_time: float = 0
    end_time: float = 0

@dataclass
class ConversationMemory:
    timestamp: str
    user_query: str
    response: str
    query_type: str
    context_tags: List[str]
    session_id: str

@dataclass 
class UserProfile:
    name: Optional[str] = None
    preferences: Dict[str, Any] = None
    interests: List[str] = None
    past_tasks: List[str] = None
    conversation_style: str = "professional"  # casual, professional, friendly
    
    def __post_init__(self):
        if self.preferences is None:
            self.preferences = {}
        if self.interests is None:
            self.interests = []
        if self.past_tasks is None:
            self.past_tasks = []

class GraphState(TypedDict):
    query: str
    query_type: str  # simple, complex_task, conversation
    nodes: Dict[str, TaskNode]
    completed_nodes: List[str]
    messages: List[Dict[str, Any]]
    current_step: int
    direct_response: str
    memory_context: str
    relevant_memories: List[ConversationMemory]

class MemoryManager:
    def __init__(self):
        self.conversation_history: List[ConversationMemory] = []
        self.user_profile = UserProfile()
        self.session_id = str(int(time.time()))
        self.max_memories = 50  # Keep last 50 conversations
    
    def add_memory(self, user_query: str, response: str, query_type: str, context_tags: List[str] = None):
        """Add a new conversation to memory"""
        if context_tags is None:
            context_tags = self._extract_context_tags(user_query, response)
        
        memory = ConversationMemory(
            timestamp=datetime.now().isoformat(),
            user_query=user_query,
            response=response,
            query_type=query_type,
            context_tags=context_tags,
            session_id=self.session_id
        )
        
        self.conversation_history.append(memory)
        
        # Keep only recent memories
        if len(self.conversation_history) > self.max_memories:
            self.conversation_history = self.conversation_history[-self.max_memories:]
        
        # Update user profile
        self._update_user_profile(user_query, query_type, context_tags)
    
    def _extract_context_tags(self, query: str, response: str) -> List[str]:
        """Extract context tags from query and response"""
        tags = []
        text = (query + " " + response).lower()
        
        # Domain tags
        domain_keywords = {
            "technology": ["ai", "software", "app", "coding", "tech", "programming", "development"],
            "business": ["marketing", "strategy", "business", "startup", "company", "revenue"],
            "events": ["workshop", "seminar", "conference", "meeting", "event", "party"],
            "education": ["learn", "study", "course", "training", "skill", "knowledge"],
            "health": ["health", "fitness", "exercise", "diet", "medical", "wellness"],
            "travel": ["travel", "trip", "vacation", "destination", "hotel", "flight"],
            "finance": ["money", "budget", "investment", "financial", "bank", "cost"]
        }
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in text for keyword in keywords):
                tags.append(domain)
        
        # Task type tags
        if any(word in text for word in ["organize", "plan", "create", "build", "develop"]):
            tags.append("task_planning")
        if any(word in text for word in ["what", "how", "why", "when", "where", "who"]):
            tags.append("information_seeking")
        
        return list(set(tags))  # Remove duplicates
    
    def _update_user_profile(self, query: str, query_type: str, context_tags: List[str]):
        """Update user profile based on conversation patterns"""
        # Update interests
        for tag in context_tags:
            if tag not in self.user_profile.interests:
                self.user_profile.interests.append(tag)
        
        # Track task types
        if query_type == "complex_task":
            task_summary = query[:50] + "..." if len(query) > 50 else query
            if task_summary not in self.user_profile.past_tasks:
                self.user_profile.past_tasks.append(task_summary)
                # Keep only recent tasks
                if len(self.user_profile.past_tasks) > 10:
                    self.user_profile.past_tasks = self.user_profile.past_tasks[-10:]
        
        # Determine conversation style
        query_lower = query.lower()
        if any(word in query_lower for word in ["please", "thank you", "thanks", "appreciate"]):
            self.user_profile.conversation_style = "polite"
        elif any(word in query_lower for word in ["hey", "hi", "sup", "cool"]):
            self.user_profile.conversation_style = "casual"
        elif len(query.split()) > 20:  # Long, detailed queries
            self.user_profile.conversation_style = "detailed"
    
    def get_relevant_memories(self, current_query: str, limit: int = 3) -> List[ConversationMemory]:
        """Retrieve relevant memories based on current query"""
        if not self.conversation_history:
            return []
        
        current_tags = self._extract_context_tags(current_query, "")
        scored_memories = []
        
        for memory in self.conversation_history:
            score = self._calculate_relevance_score(current_query, current_tags, memory)
            scored_memories.append((score, memory))
        
        # Sort by relevance score and return top memories
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        return [memory for _, memory in scored_memories[:limit]]
    
    def _calculate_relevance_score(self, current_query: str, current_tags: List[str], memory: ConversationMemory) -> float:
        """Calculate relevance score between current query and past memory"""
        score = 0.0
        
        # Recency score (more recent = higher score)
        memory_time = datetime.fromisoformat(memory.timestamp)
        hours_ago = (datetime.now() - memory_time).total_seconds() / 3600
        recency_score = max(0, 1 - (hours_ago / 168))  # Decay over a week
        score += recency_score * 0.3
        
        # Tag overlap score
        tag_overlap = len(set(current_tags) & set(memory.context_tags))
        if current_tags:
            tag_score = tag_overlap / len(current_tags)
            score += tag_score * 0.4
        
        # Text similarity score (simple keyword matching)
        query_words = set(current_query.lower().split())
        memory_words = set(memory.user_query.lower().split())
        word_overlap = len(query_words & memory_words)
        if query_words:
            text_score = word_overlap / len(query_words)
            score += text_score * 0.3
        
        return score
    
    def get_memory_context(self, relevant_memories: List[ConversationMemory]) -> str:
        """Generate memory context string for LLM"""
        if not relevant_memories:
            return ""
        
        context_parts = ["Previous conversation context:"]
        for i, memory in enumerate(relevant_memories):
            time_ago = self._time_ago(memory.timestamp)
            context_parts.append(f"{i+1}. {time_ago}: User asked '{memory.user_query[:60]}...' about {', '.join(memory.context_tags)}")
        
        # Add user profile info
        if self.user_profile.interests:
            context_parts.append(f"\nUser interests: {', '.join(self.user_profile.interests[:5])}")
        if self.user_profile.past_tasks:
            context_parts.append(f"Recent tasks: {', '.join(self.user_profile.past_tasks[:3])}")
        
        return "\n".join(context_parts)
    
    def _time_ago(self, timestamp: str) -> str:
        """Convert timestamp to human-readable time ago"""
        memory_time = datetime.fromisoformat(timestamp)
        diff = datetime.now() - memory_time
        
        if diff.days > 0:
            return f"{diff.days} days ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hours ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minutes ago"
        else:
            return "Just now"
    
    def get_personalized_greeting(self) -> str:
        """Generate a personalized greeting based on user profile"""
        greetings = []
        
        if self.user_profile.name:
            greetings.append(f"Hello {self.user_profile.name}!")
        else:
            greetings.append("Hello!")
        
        if self.user_profile.past_tasks:
            greetings.append(f"I remember we worked on {len(self.user_profile.past_tasks)} projects together.")
        
        if self.user_profile.interests:
            top_interests = self.user_profile.interests[:2]
            greetings.append(f"I see you're interested in {', '.join(top_interests)}.")
        
        return " ".join(greetings)

class EnhancedAgentOrchestrator:
    def __init__(self):
        # Initialize LLM
        try:
            self.llm = ChatGroq(model="deepseek-r1-distill-llama-70b", temperature=0.7)
        except Exception as e:
            st.error(f"Failed to initialize Groq LLM: {str(e)}")
            self.llm = None
        
        self.memory_manager = MemoryManager()
        self.graph = self._create_graph()
    
    def _classify_query(self, query: str) -> str:
        """Classify the type of query to determine appropriate handling"""
        query_lower = query.lower().strip()
        
        # Personal/memory queries
        if any(word in query_lower for word in ['remember', 'recall', 'previous', 'before', 'earlier', 'last time']):
            return "memory_query"
        
        # Simple informational queries
        simple_patterns = [
            r'\b(who is|what is|when is|where is|how is|why is)\b',
            r'\b(tell me about|explain|define|describe)\b',
            r'\b(current|latest|recent|today)\b.*\b(news|weather|time|date)\b',
            r'\b(prime minister|president|capital|population)\b',
            r'\b(meaning of|definition of)\b',
            r'\b(what does|how does)\b.*\b(work|mean)\b'
        ]
        
        # Complex task patterns
        complex_patterns = [
            r'\b(organize|plan|create|build|develop|design|manage|coordinate)\b',
            r'\b(workshop|seminar|meeting|conference|event|party|celebration)\b',
            r'\b(app|software|website|system|platform|application)\b',
            r'\b(campaign|marketing|advertising|promotion)\b',
            r'\b(project|strategy|business plan)\b'
        ]
        
        # Check for simple queries first
        for pattern in simple_patterns:
            if re.search(pattern, query_lower):
                return "simple"
        
        # Check for complex task queries
        for pattern in complex_patterns:
            if re.search(pattern, query_lower):
                return "complex_task"
        
        # Default to conversational for unclear queries
        return "conversation"
    
    def _create_graph(self) -> StateGraph:
        """Create the LangGraph workflow with memory integration"""
        workflow = StateGraph(GraphState)
        
        # Add nodes
        workflow.add_node("memory_retriever", self.retrieve_memories)
        workflow.add_node("classifier", self.classify_query)
        workflow.add_node("simple_responder", self.handle_simple_query)
        workflow.add_node("memory_responder", self.handle_memory_query)
        workflow.add_node("task_analyzer", self.analyze_complex_task)
        workflow.add_node("planner", self.create_execution_plan)
        workflow.add_node("executor", self.execute_tasks)
        workflow.add_node("coordinator", self.coordinate_agents)
        workflow.add_node("reporter", self.generate_report)
        workflow.add_node("conversational", self.handle_conversation)
        workflow.add_node("memory_saver", self.save_to_memory)
        
        # Add edges with conditional routing
        workflow.set_entry_point("memory_retriever")
        workflow.add_edge("memory_retriever", "classifier")
        
        # Conditional edges based on query type
        workflow.add_conditional_edges(
            "classifier",
            lambda state: state["query_type"],
            {
                "simple": "simple_responder",
                "memory_query": "memory_responder",
                "complex_task": "task_analyzer", 
                "conversation": "conversational"
            }
        )
        
        # All paths go to memory saver before ending
        workflow.add_edge("simple_responder", "memory_saver")
        workflow.add_edge("memory_responder", "memory_saver")
        workflow.add_edge("conversational", "memory_saver")
        workflow.add_edge("reporter", "memory_saver")
        workflow.add_edge("memory_saver", END)
        
        # Complex task path
        workflow.add_edge("task_analyzer", "planner")
        workflow.add_edge("planner", "executor")
        workflow.add_edge("executor", "coordinator")
        workflow.add_edge("coordinator", "reporter")
        
        return workflow.compile()
    
    async def retrieve_memories(self, state: GraphState) -> GraphState:
        """Retrieve relevant memories for the current query"""
        query = state["query"]
        relevant_memories = self.memory_manager.get_relevant_memories(query)
        memory_context = self.memory_manager.get_memory_context(relevant_memories)
        
        state["relevant_memories"] = relevant_memories
        state["memory_context"] = memory_context
        
        if relevant_memories:
            state["messages"].append({
                "type": "system",
                "content": f"🧠 Retrieved {len(relevant_memories)} relevant memories from our previous conversations",
                "timestamp": datetime.now().isoformat()
            })
        
        return state
    
    async def classify_query(self, state: GraphState) -> GraphState:
        """Classify the query type"""
        query = state["query"]
        query_type = self._classify_query(query)
        state["query_type"] = query_type
        
        state["messages"].append({
            "type": "system",
            "content": f"🧠 Processing query type: {query_type.replace('_', ' ').title()}",
            "timestamp": datetime.now().isoformat()
        })
        
        return state
    
    async def handle_memory_query(self, state: GraphState) -> GraphState:
        """Handle queries about previous conversations"""
        query = state["query"]
        relevant_memories = state["relevant_memories"]
        
        if not relevant_memories:
            response = "I don't have any specific memories related to that topic in our conversation history. Could you provide more details or ask me something else?"
        else:
            # Create a response based on memories
            memory_details = []
            for memory in relevant_memories:
                time_ago = self.memory_manager._time_ago(memory.timestamp)
                memory_details.append(f"- {time_ago}: You asked about '{memory.user_query}' (Topic: {', '.join(memory.context_tags)})")
            
            response = f"Here's what I remember from our previous conversations:\n\n" + "\n".join(memory_details)
            
            if self.memory_manager.user_profile.past_tasks:
                response += f"\n\nWe've also worked together on these tasks:\n"
                for task in self.memory_manager.user_profile.past_tasks[:5]:
                    response += f"• {task}\n"
        
        state["direct_response"] = response
        state["messages"].append({
            "type": "memory_response",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        return state
    
    async def handle_simple_query(self, state: GraphState) -> GraphState:
        """Handle simple informational queries with memory context"""
        query = state["query"]
        memory_context = state["memory_context"]
        
        if self.llm:
            try:
                # Enhanced prompt with memory context
                system_prompt = f"""You are a helpful and knowledgeable assistant with memory of previous conversations. 
                Answer the following question directly and concisely. Use a conversational tone that matches the user's style.
                
                {memory_context}
                
                User's conversation style: {self.memory_manager.user_profile.conversation_style}
                
                Question: {query}
                
                Answer:"""
                
                response = await self.llm.ainvoke(system_prompt)
                content = response.content if hasattr(response, 'content') else str(response)
                
                state["direct_response"] = content
                state["messages"].append({
                    "type": "direct_answer",
                    "content": content,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                error_msg = f"I apologize, but I encountered an error while processing your query: {str(e)}"
                state["direct_response"] = error_msg
                state["messages"].append({
                    "type": "error",
                    "content": error_msg,
                    "timestamp": datetime.now().isoformat()
                })
        else:
            fallback_msg = "I'm currently unable to process your query due to LLM unavailability."
            state["direct_response"] = fallback_msg
            state["messages"].append({
                "type": "error",
                "content": fallback_msg,
                "timestamp": datetime.now().isoformat()
            })
        
        return state
    
    async def handle_conversation(self, state: GraphState) -> GraphState:
        """Handle conversational queries with memory context"""
        query = state["query"]
        memory_context = state["memory_context"]
        
        if self.llm:
            try:
                # Personalized conversation prompt
                system_prompt = f"""You are a friendly and helpful conversational AI assistant with memory of previous interactions.
                Respond naturally to the user's message, incorporating relevant context from previous conversations.
                Be engaging, helpful, and maintain consistency with past interactions.
                
                {memory_context}
                
                User's preferred conversation style: {self.memory_manager.user_profile.conversation_style}
                
                User message: {query}
                
                Response:"""
                
                response = await self.llm.ainvoke(system_prompt)
                content = response.content if hasattr(response, 'content') else str(response)
                
                state["direct_response"] = content
                state["messages"].append({
                    "type": "conversation",
                    "content": content,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                error_msg = f"I apologize, but I encountered an error: {str(e)}"
                state["direct_response"] = error_msg
                state["messages"].append({
                    "type": "error", 
                    "content": error_msg,
                    "timestamp": datetime.now().isoformat()
                })
        else:
            fallback_msg = "I'd love to chat, but I'm currently having technical difficulties."
            state["direct_response"] = fallback_msg
            state["messages"].append({
                "type": "error",
                "content": fallback_msg,
                "timestamp": datetime.now().isoformat()
            })
        
        return state
    
    async def save_to_memory(self, state: GraphState) -> GraphState:
        """Save the conversation to memory"""
        query = state["query"]
        query_type = state["query_type"]
        
        # Get response content
        response_content = state.get("direct_response", "")
        if not response_content:
            # Extract response from messages if not in direct_response
            response_messages = [msg for msg in state["messages"] if msg["type"] in ["direct_answer", "conversation", "memory_response", "report"]]
            if response_messages:
                response_content = response_messages[-1]["content"]
        
        # Save to memory
        if response_content:
            self.memory_manager.add_memory(query, response_content, query_type)
            
            state["messages"].append({
                "type": "system",
                "content": f"💾 Conversation saved to memory (Total memories: {len(self.memory_manager.conversation_history)})",
                "timestamp": datetime.now().isoformat()
            })
        
        return state
    
    def decompose_task(self, query: str) -> List[TaskNode]:
        """Dynamically create task graph based on query with memory context"""
        query_lower = query.lower()
        
        # Check if user has done similar tasks before
        similar_tasks = [task for task in self.memory_manager.user_profile.past_tasks 
                        if any(word in task.lower() for word in query_lower.split()[:3])]
        
        # Workshop/Event organization
        if any(word in query_lower for word in ['workshop', 'seminar', 'meeting', 'conference']):
            base_tasks = [
                TaskNode("req_analysis", "Requirements Analyst", "Analyze workshop requirements and objectives", []),
                TaskNode("venue_booking", "Venue Coordinator", "Research and book appropriate venue", ["req_analysis"]),
                TaskNode("speaker_coord", "Speaker Coordinator", "Contact and coordinate with speakers", ["req_analysis"]),
                TaskNode("marketing", "Marketing Specialist", "Create promotional materials and campaigns", ["venue_booking", "speaker_coord"]),
                TaskNode("registration", "Registration Manager", "Set up registration system and process", ["marketing"]),
                TaskNode("logistics", "Logistics Coordinator", "Arrange equipment, catering, and materials", ["venue_booking"]),
                TaskNode("final_coord", "Event Manager", "Final coordination and event checklist", ["registration", "logistics"])
            ]
            
            # Add experience-based optimization
            if similar_tasks:
                base_tasks.insert(1, TaskNode("experience_review", "Experience Advisor", 
                                           f"Review lessons learned from previous similar projects: {', '.join(similar_tasks[:2])}", 
                                           ["req_analysis"]))
            
            return base_tasks
        
        # Software development
        elif any(word in query_lower for word in ['app', 'software', 'develop', 'build', 'code', 'website', 'system']):
            return [
                TaskNode("requirements", "Business Analyst", "Gather and document requirements", []),
                TaskNode("architecture", "Solution Architect", "Design system architecture and tech stack", ["requirements"]),
                TaskNode("ui_design", "UI/UX Designer", "Create user interface and experience design", ["requirements"]),
                TaskNode("backend_dev", "Backend Developer", "Develop server-side logic and APIs", ["architecture"]),
                TaskNode("frontend_dev", "Frontend Developer", "Implement user interface", ["ui_design", "backend_dev"]),
                TaskNode("testing", "QA Engineer", "Perform testing and quality assurance", ["frontend_dev"]),
                TaskNode("deployment", "DevOps Engineer", "Deploy to production environment", ["testing"])
            ]
        
        # Marketing campaign
        elif any(word in query_lower for word in ['marketing', 'campaign', 'promote', 'advertising', 'brand']):
            return [
                TaskNode("strategy", "Marketing Strategist", "Develop marketing strategy and goals", []),
                TaskNode("research", "Market Researcher", "Analyze target audience and competition", []),
                TaskNode("content", "Content Creator", "Create engaging content and copy", ["strategy", "research"]),
                TaskNode("design", "Creative Designer", "Design visual assets and branding", ["strategy"]),
                TaskNode("channels", "Channel Manager", "Set up and configure marketing channels", ["content", "design"]),
                TaskNode("analytics", "Analytics Specialist", "Implement tracking and measurement", ["channels"]),
                TaskNode("optimization", "Campaign Manager", "Monitor and optimize campaign performance", ["analytics"])
            ]
        
        # Party/Event planning
        elif any(word in query_lower for word in ['party', 'celebration', 'birthday', 'anniversary', 'wedding']):
            return [
                TaskNode("theme", "Event Planner", "Develop party theme and concept", []),
                TaskNode("guest_list", "Guest Coordinator", "Manage guest list and invitations", []),
                TaskNode("venue", "Venue Manager", "Secure and prepare party location", ["theme"]),
                TaskNode("catering", "Catering Coordinator", "Plan menu and arrange food service", ["guest_list", "venue"]),
                TaskNode("entertainment", "Entertainment Manager", "Book entertainment and activities", ["theme", "venue"]),
                TaskNode("decorations", "Decoration Specialist", "Plan and set up decorations", ["theme", "venue"]),
                TaskNode("photography", "Event Photographer", "Arrange photography and videography", ["entertainment"])
            ]
        
        # Business/Project planning
        elif any(word in query_lower for word in ['business', 'project', 'strategy', 'plan']):
            return [
                TaskNode("analysis", "Business Analyst", "Conduct market and feasibility analysis", []),
                TaskNode("planning", "Strategic Planner", "Create comprehensive business plan", ["analysis"]),
                TaskNode("resources", "Resource Manager", "Identify and allocate necessary resources", ["planning"]),
                TaskNode("timeline", "Project Manager", "Develop project timeline and milestones", ["resources"]),
                TaskNode("execution", "Operations Manager", "Execute planned activities", ["timeline"]),
                TaskNode("monitoring", "Quality Assurance Manager", "Monitor progress and quality", ["execution"])
            ]
        
        # Generic task breakdown
        else:
            return [
                TaskNode("analysis", "Task Analyst", "Analyze and understand the requirements", []),
                TaskNode("planning", "Project Planner", "Create detailed execution plan", ["analysis"]),
                TaskNode("resource_allocation", "Resource Coordinator", "Identify and allocate necessary resources", ["planning"]),
                TaskNode("coordination", "Team Coordinator", "Coordinate with relevant stakeholders", ["resource_allocation"]),
                TaskNode("execution", "Implementation Specialist", "Execute the planned activities", ["coordination"]),
                TaskNode("quality_check", "Quality Assurance Specialist", "Review and ensure quality standards", ["execution"])
            ]
    
    async def analyze_complex_task(self, state: GraphState) -> GraphState:
        """Analyze complex tasks with memory context"""
        query = state["query"]
        memory_context = state["memory_context"]
        
        # Create task nodes based on query
        nodes = self.decompose_task(query)
        nodes_dict = {node.id: node for node in nodes}
        
        state["nodes"] = nodes_dict
        state["completed_nodes"] = []
        state["current_step"] = 1
        
        # Enhanced analysis message with memory context
        analysis_msg = f"🎯 **Task Analysis Complete**: Breaking down '{query}' into {len(nodes)} specialized subtasks"
        if state["memory_context"]:
            analysis_msg += "\n🧠 *Incorporating insights from our previous conversations*"
        
        state["messages"].append({
            "type": "system",
            "content": analysis_msg,
            "timestamp": datetime.now().isoformat()
        })
        
        return state
    
    async def create_execution_plan(self, state: GraphState) -> GraphState:
        """Create detailed execution plan with memory-enhanced context"""
        nodes = state["nodes"]
        memory_context = state["memory_context"]
        
        # Generate execution plan
        plan_details = []
        for node in nodes.values():
            deps = node.dependencies if node.dependencies else ["No dependencies"]
            plan_details.append(f"• **{node.agent_name}**: {node.task_description}")
            if node.dependencies:
                plan_details.append(f"  └─ *Depends on: {', '.join(deps)}*")
        
        plan_content = f"📋 **Execution Plan Created:**\n\n" + "\n".join(plan_details)
        
        if memory_context:
            plan_content += f"\n\n🧠 **Leveraging Past Experience**: Using insights from previous similar projects"
        
        state["messages"].append({
            "type": "system", 
            "content": plan_content,
            "timestamp": datetime.now().isoformat()
        })
        
        state["current_step"] = 2
        return state
    
    async def execute_tasks(self, state: GraphState) -> GraphState:
        """Execute tasks based on dependencies"""
        nodes = state["nodes"]
        completed = set(state["completed_nodes"])
        
        # Find ready nodes (dependencies satisfied)
        ready_nodes = [
            node for node in nodes.values() 
            if node.status == "pending" and all(dep in completed for dep in node.dependencies)
        ]
        
        # Execute ready nodes
        for node in ready_nodes:
            await self._execute_single_task(node, state)
            completed.add(node.id)
        
        state["completed_nodes"] = list(completed)
        state["current_step"] = 3
        return state
    
    async def _execute_single_task(self, node: TaskNode, state: GraphState):
        """Execute a single task node with memory-enhanced prompts"""
        node.status = "running"
        node.start_time = time.time()
        
        # Add start message
        state["messages"].append({
            "type": "agent_start",
            "content": f"🚀 **{node.agent_name}** is working on: {node.task_description}",
            "agent": node.agent_name,
            "task_id": node.id,
            "timestamp": datetime.now().isoformat()
        })
        
        # Simulate work with realistic delay
        await asyncio.sleep(1.5)  # Faster execution
        
        # Generate task result with memory context
        if self.llm:
            try:
                memory_context = state["memory_context"]
                prompt = f"""You are a {node.agent_name}. You have just completed the task: "{node.task_description}".
                
                {memory_context}
                
                Provide a brief, professional summary of what you accomplished (2-3 sentences max). 
                Be specific and realistic about the deliverables or outcomes.
                If there's relevant context from previous conversations, incorporate those learnings.
                
                Task: {node.task_description}
                
                Summary of completion:"""
                
                result = await self.llm.ainvoke(prompt)
                content = result.content if hasattr(result, 'content') else str(result)
                node.result = content[:150] + "..." if len(content) > 150 else content
            except:
                node.result = f"Successfully completed: {node.task_description.lower()}"
        else:
            node.result = f"Successfully completed: {node.task_description.lower()}"
        
        node.status = "completed"
        node.end_time = time.time()
        
        # Add completion message
        state["messages"].append({
            "type": "agent_complete",
            "content": f"✅ **{node.agent_name}** completed their task",
            "result": node.result,
            "agent": node.agent_name,
            "task_id": node.id,
            "duration": round(node.end_time - node.start_time, 2),
            "timestamp": datetime.now().isoformat()
        })
    
    async def coordinate_agents(self, state: GraphState) -> GraphState:
        """Coordinate between agents and handle dependencies"""
        nodes = state["nodes"]
        total_nodes = len(nodes)
        completed_count = len(state["completed_nodes"])
        
        # Check if all tasks completed
        if completed_count < total_nodes:
            # Find remaining tasks
            remaining = [node for node in nodes.values() if node.status != "completed"]
            
            # Execute remaining tasks with satisfied dependencies
            for node in remaining:
                if all(dep in state["completed_nodes"] for dep in node.dependencies):
                    await self._execute_single_task(node, state)
                    state["completed_nodes"].append(node.id)
        
        state["current_step"] = 4
        return state
    
    async def generate_report(self, state: GraphState) -> GraphState:
        """Generate final execution report with memory integration"""
        nodes = state["nodes"]
        total_time = sum(node.end_time - node.start_time for node in nodes.values() if node.status == "completed")
        
        report = f"""## 🎉 Task Orchestration Complete!

### 📊 **Execution Summary**
- **Total Specialists**: {len(nodes)}
- **Completed Tasks**: {len(state['completed_nodes'])}
- **Total Execution Time**: {total_time:.1f} seconds

### 🤖 **Agent Deliverables**
"""
        
        for node in nodes.values():
            report += f"\n**{node.agent_name}**\n*{node.result}*\n"
        
        report += f"\n---\n✨ **All specialists have successfully coordinated to complete:** *\"{state['query']}\"*"
        
        # Add memory note
        similar_tasks = len([task for task in self.memory_manager.user_profile.past_tasks 
                           if any(word in task.lower() for word in state['query'].lower().split()[:3])])
        if similar_tasks > 0:
            report += f"\n\n🧠 *This experience has been added to our shared memory for future similar projects.*"
        
        state["messages"].append({
            "type": "report",
            "content": report,
            "timestamp": datetime.now().isoformat()
        })
        
        state["current_step"] = 5
        return state
    
    async def process_query(self, query: str) -> tuple[List[Dict[str, Any]], str]:
        """Process a query through the LangGraph workflow"""
        initial_state = GraphState(
            query=query,
            query_type="",
            nodes={},
            completed_nodes=[],
            messages=[],
            current_step=0,
            direct_response="",
            memory_context="",
            relevant_memories=[]
        )
        
        # Execute the graph
        result = await self.graph.ainvoke(initial_state)
        return result["messages"], result.get("direct_response", "")

# Streamlit App with Memory Features
def main():
    st.set_page_config(
        page_title="🧠 Memory-Enhanced Agentic Assistant",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling - FIXED MEMORY SYSTEM BACKGROUND
    st.markdown("""
    <style>
    .main-header {
        text-align: center; 
        padding: 2rem; 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); 
        border-radius: 15px; 
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .memory-stats {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: 1px solid #667eea;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .memory-stats strong {
        color: #ffffff;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
    }
    .user-profile {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1 style="color: white; margin: 0; font-size: 2.5rem;"> Agentic Assistant</h1>
        <p style="color: white; opacity: 0.9; margin: 0; font-size: 1.1rem;">Intelligent Task Orchestration with Conversational Memory</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize orchestrator
    if 'orchestrator' not in st.session_state:
        st.session_state.orchestrator = EnhancedAgentOrchestrator()
    
    # Initialize chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        
        # Add welcome message with personalized greeting
        greeting = st.session_state.orchestrator.memory_manager.get_personalized_greeting()
        welcome_msg = f"{greeting} I'm your AI assistant. I can help with simple questions, complex task planning, and I'll remember our conversations for better assistance over time."
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": welcome_msg
        })
    
    # Memory status in header area
    memory_manager = st.session_state.orchestrator.memory_manager
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("💭 Memories", len(memory_manager.conversation_history))
    with col2:
        st.metric("🎯 Interests", len(memory_manager.user_profile.interests))
    with col3:
        st.metric("📋 Past Tasks", len(memory_manager.user_profile.past_tasks))
    
    # Example queries in tabs
    tab1, tab2, tab3, tab4 = st.tabs(["💬 Quick Questions", "🎯 Complex Tasks", "💡 Creative Ideas", "🧠 Memory Queries"])
    
    with tab1:
        st.markdown("**Try these simple questions:**")
        simple_examples = [
            "Who is the Prime Minister of India?",
            "What is artificial intelligence?", 
            "Tell me about climate change",
            "How does blockchain work?",
            "What's the capital of Japan?"
        ]
        cols = st.columns(3)
        for i, query in enumerate(simple_examples):
            if cols[i % 3].button(query, key=f"simple_{i}"):
                st.session_state.query_input = query
    
    with tab2:
        st.markdown("**Complex task orchestration:**")
        complex_examples = [
            "Organize a robotics workshop for 50 people",
            "Develop a mobile banking application",
            "Create a marketing campaign for eco-friendly products", 
            "Plan a wedding ceremony for 200 guests",
            "Build an e-commerce website from scratch"
        ]
        cols = st.columns(2)
        for i, query in enumerate(complex_examples):
            if cols[i % 2].button(query, key=f"complex_{i}"):
                st.session_state.query_input = query
    
    with tab3:
        st.markdown("**Creative and business ideas:**")
        creative_examples = [
            "Design a sustainable city transportation system",
            "Create a social media strategy for a startup",
            "Plan a tech conference about future of AI"
        ]
        for i, query in enumerate(creative_examples):
            if st.button(query, key=f"creative_{i}"):
                st.session_state.query_input = query
    
    with tab4:
        st.markdown("**Test memory capabilities:**")
        memory_examples = [
            "What did we discuss last time?",
            "Remember what projects we worked on before?",
            "What topics am I most interested in?",
            "Show me my conversation history",
            "What tasks have I asked you to help with previously?"
        ]
        for i, query in enumerate(memory_examples):
            if st.button(query, key=f"memory_{i}"):
                st.session_state.query_input = query
    
    # Chat interface
    st.markdown("### 💬 Chat with Memory-Enhanced AI")
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if message["role"] == "assistant" and "metadata" in message:
                    # Display structured agent messages
                    metadata = message["metadata"]
                    if metadata["type"] == "agent_start":
                        st.markdown(f"🚀 {metadata['content']}")
                    elif metadata["type"] == "agent_complete":
                        st.markdown(f"✅ {metadata['content']}")
                        if "result" in metadata:
                            st.markdown(f"*📋 Result: {metadata['result']}*")
                    elif metadata["type"] == "system":
                        st.info(metadata['content'])
                    elif metadata["type"] == "report":
                        st.markdown(metadata['content'])
                    elif metadata["type"] == "direct_answer":
                        st.markdown(f"💡 {metadata['content']}")
                    elif metadata["type"] == "conversation":
                        st.markdown(metadata['content'])
                    elif metadata["type"] == "memory_response":
                        st.markdown(f"🧠 {metadata['content']}")
                    elif metadata["type"] == "error":
                        st.error(metadata['content'])
                else:
                    st.markdown(message["content"])
    
    # Query input
    query = st.chat_input("Ask me anything - I'll remember our conversation for better help...")
    
    # Handle example button clicks
    if hasattr(st.session_state, 'query_input'):
        query = st.session_state.query_input
        delattr(st.session_state, 'query_input')
    
    if query:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": query})
        
        # Process query
        with st.chat_message("user"):
            st.markdown(query)
        
        with st.chat_message("assistant"):
            with st.spinner("🧠 Processing with memory context..."):
                try:
                    messages, direct_response = asyncio.run(st.session_state.orchestrator.process_query(query))
                    
                    # Handle direct responses (simple queries, memory queries, conversations)
                    if direct_response:
                        st.markdown(f"💡 {direct_response}")
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": direct_response
                        })
                    
                    # Display structured messages for complex tasks
                    for msg in messages:
                        if msg["type"] == "system":
                            st.info(msg['content'])
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": msg['content'],
                                "metadata": msg
                            })
                        elif msg["type"] in ["agent_start", "agent_complete"]:
                            if msg["type"] == "agent_start":
                                st.markdown(f"🚀 {msg['content']}")
                            else:
                                st.markdown(f"✅ {msg['content']}")
                                if "result" in msg:
                                    st.markdown(f"*📋 Result: {msg['result']}*")
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": msg['content'],
                                "metadata": msg
                            })
                        elif msg["type"] == "report":
                            st.markdown(msg['content'])
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": msg['content'],
                                "metadata": msg
                            })
                        elif msg["type"] in ["direct_answer", "conversation", "memory_response"]:
                            prefix = "💡" if msg["type"] == "direct_answer" else "🧠" if msg["type"] == "memory_response" else ""
                            st.markdown(f"{prefix} {msg['content']}")
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": msg['content'],
                                "metadata": msg
                            })
                        elif msg["type"] == "error":
                            st.error(msg['content'])
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": msg['content'],
                                "metadata": msg
                            })
                        
                        # Small delay for visual effect
                        if msg["type"] in ["agent_start", "agent_complete"]:
                            time.sleep(0.3)
                        
                except Exception as e:
                    error_msg = f"❌ I encountered an error while processing your request: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
    
    # Enhanced sidebar with memory information
    with st.sidebar:
        st.markdown("### 🧠 **Memory System**")
        
        memory_manager = st.session_state.orchestrator.memory_manager
        
        # Memory statistics with FIXED BACKGROUND
        st.markdown("""
        <div class="memory-stats">
            <strong>📊 Memory Statistics</strong><br>
            • Conversation memories stored<br>
            • Learning from interaction patterns<br>
            • Context-aware responses<br>
            • Personalized experience
        </div>
        """, unsafe_allow_html=True)
        
        # User profile section
        if memory_manager.user_profile.interests or memory_manager.user_profile.past_tasks:
            st.markdown("### 👤 **Your Profile**")
            
            if memory_manager.user_profile.interests:
                st.markdown(f"**🎯 Interests:** {', '.join(memory_manager.user_profile.interests[:5])}")
            
            if memory_manager.user_profile.past_tasks:
                st.markdown("**📋 Recent Tasks:**")
                for task in memory_manager.user_profile.past_tasks[:3]:
                    st.markdown(f"• {task}")
            
            st.markdown(f"**💬 Style:** {memory_manager.user_profile.conversation_style.title()}")
        
        st.markdown("---")
        
        st.markdown("### 🔧 **System Capabilities**")
        st.markdown("""
        **🎯 Query Types:**
        - 💬 Simple Q&A with context
        - 🤖 Complex task orchestration  
        - 💭 Contextual conversation
        - 🧠 Memory-based queries
        
        **🛠️ Memory Features:**
        - **Conversation history** tracking
        - **User profile** learning
        - **Context-aware** responses
        - **Experience-based** optimization
        - **Personalized** interactions
        
        **🎪 Specialized Domains:**
        - 📅 Event & workshop organization
        - 💻 Software development  
        - 📈 Marketing campaigns
        - 🎉 Celebration planning
        - 🏢 Business strategy
        - 🔧 General task breakdown
        """)
        
        # Connection status
        if st.session_state.orchestrator.llm:
            st.success("🟢 Groq LLM Connected")
        else:
            st.error("🔴 LLM Connection Failed")
        
        st.markdown("---")
        
        # Memory management buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Chat", type="secondary"):
                st.session_state.messages = [st.session_state.messages[0]]  # Keep welcome message
                st.rerun()
        
        with col2:
            if st.button("🧠 Reset Memory", type="secondary"):
                st.session_state.orchestrator.memory_manager = MemoryManager()
                st.success("Memory reset!")
                st.rerun()
        
        # Export memory option
        if st.button("📥 Export Memory", type="secondary"):
            memory_data = {
                "conversation_history": [asdict(memory) for memory in memory_manager.conversation_history],
                "user_profile": asdict(memory_manager.user_profile),
                "session_id": memory_manager.session_id,
                "export_time": datetime.now().isoformat()
            }
            
            st.download_button(
                label="💾 Download Memory Data",
                data=json.dumps(memory_data, indent=2),
                file_name=f"ai_memory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        st.markdown("---")
        st.markdown("*💡 **Tip**: I learn from our conversations to provide better, more personalized assistance over time!*")

if __name__ == "__main__":
    main()

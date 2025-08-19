def decompose_task(query: str):
    if "workshop" in query.lower():
        return [
            ("Book venue", "venue"),
            ("Email coordinator", "email"),
            ("Prepare poster", "poster")
        ]
    elif "birthday" in query.lower():
        return [
            ("Book cake", "default"),
            ("Send invitations", "email"),
            ("Arrange decoration", "default")
        ]
    else:
        return [("Handle general task", "default")]
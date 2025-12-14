class TripToolContext:
    def __init__(self, session_service, app_name, user_id, session_id):
        self.session_service = session_service
        self.app_name = app_name
        self.user_id = user_id
        self.session_id = session_id
        self.state = {}

    async def load_state(self):
        session = await self.session_service.get_session(
            self.app_name,
            self.user_id,
            self.session_id
        )
        self.state = session.state if session else {}

    async def save_state(self):
        await self.session_service.update_session_state(
            self.app_name,
            self.user_id,
            self.session_id,
            self.state
        )
    
    def get_state_value(self, key: str, default=None):
        """Get a value from state"""
        return self.state.get(key, default)
    
    def set_state_value(self, key: str, value):
        """Set a value in state"""
        self.state[key] = value

    def __repr__(self):
        return (
            f"<TripToolContext user_id={self.user_id}, "
            f"session_id={self.session_id}, app_name={self.app_name}>"
        )
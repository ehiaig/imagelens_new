class ApiError(Exception):
    def __init__(self, error_description, error_type="invalid_data", error_code=400):
        self.error_code = error_code
        self.error_type = error_type
        self.error_description = error_description

    def to_response(self):
        return (
            {
                "error_type": self.error_type,
                "error_description": self.error_description,
            },
            self.error_code,
        )


# def handle_app_exceptions(e): 
#     return e.to_response()
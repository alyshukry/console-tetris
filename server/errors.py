class AppError(Exception):
    status_code = 400
    detail = "Bad request"


class RoomNotFound(AppError):
    status_code = 404
    detail = "No such room"


class WrongPassword(AppError):
    status_code = 403
    detail = "Wrong password"


class RoomNameTaken(AppError):
    status_code = 409
    detail = "That name is already hosting a room"


class RoomFull(AppError):
    status_code = 409
    detail = "Room is full"


class RoomInProgress(AppError):
    status_code = 409
    detail = "Game already started"


class UserNotFound(AppError):
    status_code = 404
    detail = "User not found"


class UsernameTaken(AppError):
    status_code = 409
    detail = "Username is already taken"


class InvalidCredentials(AppError):
    status_code = 401
    detail = "Invalid username or password"
    
class InvalidToken(AppError):
    status_code = 401
    detail = "Invalid token"

class TokenExpired(AppError):
    status_code = 401
    detail = "Token expired"
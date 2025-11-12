from enum import Enum


class UserRole(str, Enum):
    student = "student"
    teacher = "teacher"
    admin = "admin"


class LevelEducation(str, Enum):
    bachelor = "bachelor"
    master = "master"
    specialist = "specialist"


class Faculty(str, Enum):
    fit = "fit"
    fpi = "fpi"
    econ = "economics"
    other = "other"

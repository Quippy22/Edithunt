from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import (
    UserAttributeSimilarityValidator as BaseUserAttributeSimilarityValidator,
    MinimumLengthValidator as BaseMinimumLengthValidator,
    CommonPasswordValidator as BaseCommonPasswordValidator,
    NumericPasswordValidator as BaseNumericPasswordValidator,
)

class UserAttributeSimilarityValidator(BaseUserAttributeSimilarityValidator):
    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except ValidationError:
            raise ValidationError(
                "Parola nu poate fi prea asemănătoare cu celelalte informații personale.",
                code='password_too_similar',
            )

    def get_help_text(self):
        return "Parola nu poate fi prea asemănătoare cu celelalte informații personale."

class MinimumLengthValidator(BaseMinimumLengthValidator):
    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except ValidationError:
            raise ValidationError(
                f"Parola trebuie să conțină cel puțin {self.min_length} caractere.",
                code='password_too_short',
                params={'min_length': self.min_length},
            )

    def get_help_text(self):
        return f"Parola trebuie să conțină cel puțin {self.min_length} caractere."

class CommonPasswordValidator(BaseCommonPasswordValidator):
    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except ValidationError:
            raise ValidationError(
                "Parola nu poate fi o parolă utilizată frecvent.",
                code='password_too_common',
            )

    def get_help_text(self):
        return "Parola nu poate fi o parolă utilizată frecvent."

class NumericPasswordValidator(BaseNumericPasswordValidator):
    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except ValidationError:
            raise ValidationError(
                "Parola nu poate fi formată doar din cifre.",
                code='password_entirely_numeric',
            )

    def get_help_text(self):
        return "Parola nu poate fi formată doar din cifre."

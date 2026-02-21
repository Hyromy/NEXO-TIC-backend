from django.test import TestCase

from utils import (
    randomizer,
    validator,
)

class ValidatorTestCase(TestCase):
    """Utils package, validator module test cases"""
    
    def test_email_simple(self):
        """Accept a simple valid email"""
        
        self.assertTrue(
            validator.is_email("user@example.com")
        )
    
    def test_email_with_dots(self):
        """Accept emails with dots in the username"""
        
        self.assertTrue(
            validator.is_email("user.name@example.com")
        )
    
    def test_email_with_numbers(self):
        """Accept emails with numbers in the username"""
        
        self.assertTrue(
            validator.is_email("user123@example.com")
        )
    
    def test_email_with_subdomain(self):
        """Accept emails with subdomains"""
        
        self.assertTrue(
            validator.is_email("user@mail.example.com")
        )
    
    def test_email_without_at(self):
        """Reject emails without @ symbol"""
        
        self.assertFalse(
            validator.is_email("userexample.com")
        )
    
    def test_email_without_domain(self):
        """Reject emails without domain"""
        
        self.assertFalse(
            validator.is_email("user@")
        )
    
    def test_email_without_extension(self):
        """Reject emails without extension"""
        
        self.assertFalse(
            validator.is_email("user@example")
        )
    
    def test_email_starts_with_number(self):
        """Reject emails that start with a number"""
        
        self.assertFalse(
            validator.is_email("123user@example.com")
        )
    
    def test_email_empty(self):
        """Reject empty strings as emails"""
        
        self.assertFalse(
            validator.is_email("")
        )
    
    def test_email_with_spaces(self):
        """Reject emails with spaces"""
        
        self.assertFalse(
            validator.is_email("user name@example.com")
        )

class RandomizerTestCase(TestCase):
    """Utils package, randomizer module test cases"""
    
    def test_default_length(self):
        """Check default password length (8 characters)"""
        
        password = randomizer.generate_password()
        self.assertEqual(len(password), 8)
    
    def test_custom_length(self):
        """Check custom password length (16 characters)"""
        
        password = randomizer.generate_password(size = 16)
        self.assertEqual(len(password), 16)
    
    def test_only_lowercase_by_default(self):
        """Check that by default it generates only lowercase letters"""
        
        password = randomizer.generate_password(size = 100)
        self.assertTrue(password.islower())
        self.assertTrue(password.isalpha())
    
    def test_include_uppercase(self):
        """Check that it includes uppercase letters when requested"""
        
        password = randomizer.generate_password(
            size = 100,
            use_upper = True
        )
        self.assertTrue(any(c.isupper() for c in password))
    
    def test_include_numbers(self):
        """Check that it includes numbers when requested"""

        password = randomizer.generate_password(
            size = 100,
            use_numbers = True
        )
        self.assertTrue(any(c.isdigit() for c in password))
    
    def test_include_special_chars(self):
        """Check default special characters"""

        password = randomizer.generate_password(
            size = 100,
            use_special_chars = True
        )
        special = "!@#$%^&*()_-+="
        self.assertTrue(any(c in special for c in password))
    
    def test_custom_special_chars(self):
        """Check that it includes only the specified special characters"""

        password = randomizer.generate_password(
            size = 100,
            use_special_chars = "@#$"
        )
        has_special = any(c in "@#$" for c in password)
        has_other_special = any(c in "!%^&*()_-+=" for c in password)

        self.assertTrue(has_special)
        self.assertFalse(has_other_special)
    
    def test_combinacion_completa(self):
        """Check that it generates a password with all character types when requested"""

        password = randomizer.generate_password(
            size = 200,
            use_upper = True,
            use_numbers = True,
            use_special_chars = True
        )

        self.assertEqual(len(password), 200)
        self.assertTrue(any(c.islower() for c in password))
        self.assertTrue(any(c.isupper() for c in password))
        self.assertTrue(any(c.isdigit() for c in password))
        self.assertTrue(any(c in "!@#$%^&*()_-+=" for c in password))
    
    def test_passwords_diferentes(self):
        """Check that it generates different passwords (random)"""

        password1 = randomizer.generate_password(size = 20)
        password2 = randomizer.generate_password(size = 20)

        self.assertNotEqual(password1, password2)

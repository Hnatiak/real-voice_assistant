import pyautogui
import time
from pynput.keyboard import Controller, Key


def write_functions(language):
    keyboard = Controller()
    # Генерація функцій для різних мов програмування
    if language == "python":
        code = """
def greet(name):
    print("Hello, " + name + "!")
greet("World")
"""
    elif language == "javascript":
        code = """
function greet(name) {
    console.log("Hello, " + name + "!");
}
greet("World");
"""
    elif language == "java":
        code = """
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
"""
    elif language == "cpp":
        code = """
#include <iostream>
using namespace s
int main() {
    cout << "Hello, World!" << endl;
    return 0;
}
"""
    else:
        return "Мова програмування не розпізнана!"
    
    for char in code:
        keyboard.type(char)
        time.sleep(0.1)  # Невелика пауза між символами

    pyautogui.press("enter")   # Натискаємо Enter
    return code

# def write_functions(language):
#     """
#     Функція генерує шаблон функції для різних мов програмування.
    
#     :param language: Назва мови програмування (наприклад, "python", "javascript", "java").
#     :return: Строка з шаблоном функції для вказаної мови програмування.
#     """
    
#     # Генерація функції для Python
#     if language.lower() == "python":
#         return """
# def example_function():
#     # Ваш код тут
#     print("Це функція на Python")
#         """
    
#     # Генерація функції для JavaScript
#     elif language.lower() == "javascript":
#         return """
# function exampleFunction() {
#     // Ваш код тут
#     console.log("Це функція на JavaScript");
# }
#         """
    
#     # Генерація функції для Java
#     elif language.lower() == "java":
#         return """
# public class Main {
#     public static void main(String[] args) {
#         exampleFunction();
#     }
    
#     public static void exampleFunction() {
#         // Ваш код тут
#         System.out.println("Це функція на Java");
#     }
# }
#         """
    
#     # Генерація функції для C#
#     elif language.lower() == "c#":
#         return """
# using System;

# class Program {
#     static void Main() {
#         ExampleFunction();
#     }

#     static void ExampleFunction() {
#         // Ваш код тут
#         Console.WriteLine("Це функція на C#");
#     }
# }
#         """
    
#     # Генерація функції для C++
#     elif language.lower() == "cpp":
#         return """
# #include <iostream>

# void exampleFunction() {
#     // Ваш код тут
#     std::cout << "Це функція на C++" << std::endl;
# }

# int main() {
#     exampleFunction();
#     return 0;
# }
#         """
    
#     # Якщо мова не підтримується
#     else:
#         return "Ця мова не підтримується."
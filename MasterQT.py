import sys
import os
import random
from PyQt6.QtWidgets import QApplication, QGridLayout, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QStackedWidget
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt


def resource_path(relative_path):
    """Obtenir le chemin absolu d'une ressource, fonctionne pour le script et l'exécutable."""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

class MainMenu(QWidget):
    """Fenêtre principale pour choisir le mode."""
    def __init__(self, switch_mode_callback):
        super().__init__()

        self.layout = QVBoxLayout()

        # Titre
        self.title_label = QLabel("Bienvenue dans le Jeu de Robot calculateur !")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title_label)

        # Bouton pour le mode entraînement
        self.train_button = QPushButton("Mode Entraînement")
        self.train_button.clicked.connect(lambda: switch_mode_callback("train"))
        self.layout.addWidget(self.train_button)

        # Bouton pour le mode test
        self.test_button = QPushButton("Mode Test")
        self.test_button.clicked.connect(lambda: switch_mode_callback("test"))
        self.layout.addWidget(self.test_button)

        self.calculator_button = QPushButton("Mode Calculatrice")
        self.calculator_button.clicked.connect(lambda: switch_mode_callback("calculator"))
        self.layout.addWidget(self.calculator_button)

        self.setLayout(self.layout)


class RobotGame(QWidget):
    """Jeu principal avec les modes entraînement et test."""
    def __init__(self, mode, switch_back_callback):
        super().__init__()

        self.mode = mode
        self.switch_back_callback = switch_back_callback

        self.setWindowTitle(f"Jeu de Robot - Mode {self.mode.capitalize()}")
        self.setGeometry(100, 100, 400, 300)

        # Layout principal
        self.layout = QVBoxLayout()
        self.score = 0
        self.numbQuestion = 0
        self.max_questions = 20 if self.mode == "test" else None  # Limite de questions pour le mode test

        # Affichage du robot
        self.robot_label = QLabel(self)
        self.robot_pixmap = QPixmap(resource_path("./img/neutre.png"))  # Assurez-vous que l'image est dans le bon dossier
        self.robot_pixmap = self.robot_pixmap.scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio)
        self.robot_label.setPixmap(self.robot_pixmap)
        self.robot_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.robot_label)

        # Générer la première opération aléatoire
        self.generate_new_question()

        # Affichage de l'opération
        self.operation_label = QLabel(f"Quel est le résultat de {self.num1} {self.operation} {self.num2} ?", self)
        self.layout.addWidget(self.operation_label)

        # Affichage du score (uniquement pour le mode test)
        if self.mode == "test":
            self.affiche_score = QLabel(f"Score : {self.score}/{self.numbQuestion}", self)
            self.layout.addWidget(self.affiche_score)

        # Champ de saisie de la réponse
        self.answer_input = QLineEdit(self)
        self.answer_input.returnPressed.connect(self.check_answer)
        self.layout.addWidget(self.answer_input)

        # Bouton pour vérifier la réponse
        self.check_button = QPushButton("Vérifier", self)
        self.check_button.clicked.connect(self.check_answer)
        self.layout.addWidget(self.check_button)

        # Bouton "Suivant" (uniquement pour le mode entraînement)
        if self.mode == "train":
            self.next_button = QPushButton("Suivant", self)
            self.next_button.clicked.connect(self.next_question)
            self.next_button.setVisible(False)  # Cacher le bouton par défaut
            self.layout.addWidget(self.next_button)

        # Zone de résultat
        self.result_label = QLabel("", self)
        self.layout.addWidget(self.result_label)

        # Bouton pour revenir au menu principal
        self.back_button = QPushButton("Retour au Menu Principal", self)
        self.back_button.clicked.connect(self.switch_back_callback)
        self.layout.addWidget(self.back_button)

        # Configuration du layout
        self.setLayout(self.layout)

    def generate_new_question(self):
        """Génère une nouvelle question mathématique."""
        self.num1 = random.randint(0, 10)
        self.num2 = random.randint(0, 10)
        self.operation = random.choice(["+", "-", "*"])
        while self.operation == "-" and self.num1 < self.num2:
            self.num1 = random.randint(0, 10)
            self.num2 = random.randint(0, 10)

        self.correct_answer = self.compute_answer()

    def compute_answer(self):
        """Calcule la réponse correcte en fonction de l'opération."""
        if self.operation == "+":
            return self.num1 + self.num2
        elif self.operation == "-":
            return self.num1 - self.num2
        elif self.operation == "*":
            return self.num1 * self.num2

    def check_answer(self):
        """Vérifie la réponse donnée par l'utilisateur."""
        try:
            user_answer = int(self.answer_input.text())
            if user_answer == self.correct_answer:
                self.result_label.setText("Bravo ! Vous avez trouvé la bonne réponse.")
                self.robot_pixmap = QPixmap(resource_path("./img/happy.png"))
                if self.mode == "test":
                    self.score += 1
                if self.mode == "train":
                    self.next_button.setVisible(False)  # Cacher le bouton "Suivant" si la réponse est correcte
            else:
                self.result_label.setText("Dommage ! Essayez encore.")
                self.robot_pixmap = QPixmap(resource_path("./img/triste.png"))
                if self.mode == "train":
                    self.next_button.setVisible(True)  # Afficher le bouton "Suivant" si la réponse est incorrecte

            self.robot_pixmap = self.robot_pixmap.scaled(self.robot_label.width(), self.robot_label.height(), Qt.AspectRatioMode.KeepAspectRatio)
            self.robot_label.setPixmap(self.robot_pixmap)

            if self.mode == "test":
                self.numbQuestion += 1
                self.affiche_score.setText(f"Score : {self.score}/{self.numbQuestion}")
                if self.numbQuestion >= self.max_questions:
                    self.end_test()
                    return

            # Générer une nouvelle question uniquement en mode test ou si la réponse est correcte
            if self.mode == "test" or user_answer == self.correct_answer:
                self.generate_new_question()
                self.operation_label.setText(f"Quel est le résultat de {self.num1} {self.operation} {self.num2} ?")
                self.answer_input.clear()
        except ValueError:
            self.result_label.setText("Veuillez entrer un nombre valide.")

    def next_question(self):
        """Passe à la question suivante (uniquement pour le mode entraînement)."""
        self.generate_new_question()
        self.operation_label.setText(f"Quel est le résultat de {self.num1} {self.operation} {self.num2} ?")
        self.answer_input.clear()
        self.result_label.setText("")  # Réinitialiser le message de résultat
        self.robot_pixmap = QPixmap(resource_path("./img/neutre.png"))
        self.robot_pixmap = self.robot_pixmap.scaled(self.robot_label.width(), self.robot_label.height(), Qt.AspectRatioMode.KeepAspectRatio)
        self.robot_label.setPixmap(self.robot_pixmap)
        self.next_button.setVisible(False)  # Cacher le bouton "Suivant" après avoir généré une nouvelle question

    def end_test(self):
        """Affiche un message de fin de test et désactive les interactions."""
        self.result_label.setText(f"Test terminé ! Votre score final est de {self.score}/{self.max_questions}.")
        self.answer_input.setDisabled(True)
        self.check_button.setDisabled(True)

class CalculatorMode(QWidget):
    """Mode Calculatrice pour effectuer des opérations."""
    def __init__(self, switch_back_callback):
        super().__init__()

        self.switch_back_callback = switch_back_callback

        # Configuration de la fenêtre
        self.setWindowTitle("Mode Calculatrice")
        self.setGeometry(100, 100, 400, 300)

        # Layout principal
        self.layout = QVBoxLayout()

        # Tête du robot
        self.robot_label = QLabel(self)
        self.robot_pixmap = QPixmap(resource_path("./img/neutre.png"))  # Assurez-vous que l'image est dans le bon dossier
        self.robot_pixmap = self.robot_pixmap.scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio)
        self.robot_label.setPixmap(self.robot_pixmap)
        self.robot_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.robot_label)

        # Zone d'affichage pour les calculs
        self.display = QLineEdit(self)
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setStyleSheet("font-size: 18px; padding: 5px;")
        self.display.returnPressed.connect(self.calculate_result)  # Calculer lorsque l'utilisateur appuie sur Entrée
        self.layout.addWidget(self.display)

        # Layout pour les boutons (grille)
        self.buttons_layout = QGridLayout()
        self.create_buttons()
        self.layout.addLayout(self.buttons_layout)

        # Bouton pour revenir au menu principal
        self.back_button = QPushButton("Retour au Menu Principal", self)
        self.back_button.setStyleSheet("font-size: 14px; padding: 5px;")
        self.back_button.clicked.connect(self.switch_back_callback)
        self.layout.addWidget(self.back_button)

        # Configuration du layout
        self.setLayout(self.layout)

    def create_buttons(self):
        """Crée les boutons de la calculatrice."""
        buttons = [
            ['7', '8', '9', '/'],
            ['4', '5', '6', '*'],
            ['1', '2', '3', '-'],
            ['0', '.', '=', '+']
        ]

        # Ajouter les boutons à la grille
        for row, row_values in enumerate(buttons):
            for col, button_text in enumerate(row_values):
                button = QPushButton(button_text, self)
                button.setStyleSheet("font-size: 14px; padding: 8px;")
                button.clicked.connect(lambda checked, text=button_text: self.on_button_click(text))
                self.buttons_layout.addWidget(button, row, col)

        # Ajouter un bouton "C" pour effacer tout
        clear_button = QPushButton("C", self)
        clear_button.setStyleSheet("font-size: 14px; padding: 8px; background-color: red; color: white;")
        clear_button.clicked.connect(lambda: self.display.clear())
        self.buttons_layout.addWidget(clear_button, 4, 0, 1, 2)  # Occupe deux colonnes

        # Ajouter un bouton "Effacer" pour supprimer le dernier caractère
        delete_button = QPushButton("Effacer", self)
        delete_button.setStyleSheet("font-size: 14px; padding: 8px; background-color: orange; color: white;")
        delete_button.clicked.connect(self.delete_last_character)
        self.buttons_layout.addWidget(delete_button, 4, 2, 1, 2)  # Occupe deux colonnes

    def on_button_click(self, text):
        """Gère les clics sur les boutons de la calculatrice."""
        if text == '=':
            self.calculate_result()
        else:
            # Ajoute le texte du bouton à l'affichage
            self.display.setText(self.display.text() + text)

    def calculate_result(self):
        """Calcule le résultat de l'expression dans l'affichage."""
        try:
            # Évalue l'expression mathématique
            result = eval(self.display.text())
            self.display.setText(str(result))
            imglist = ["1.png", "2.png", "3.png", "4.png", "5.png", "happy.png", "neutre.png"]
            imgrandom = random.choice(imglist)
            self.robot_pixmap = QPixmap(resource_path(f"./img/{imgrandom}"))
            self.robot_pixmap = self.robot_pixmap.scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio)
            self.robot_label.setPixmap(self.robot_pixmap)

        except Exception:
            self.display.setText("Erreur")

    def delete_last_character(self):
        """Supprime le dernier caractère de l'affichage."""
        current_text = self.display.text()
        self.display.setText(current_text[:-1])

class MainWindow(QMainWindow):
    """Fenêtre principale avec gestion des modes."""
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Jeu de Robot calculateur")
        self.setFixedSize(800, 600)  # Fixer la taille de la fenêtre à 800x600

        # Gestionnaire de widgets empilés
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        # Ajouter un widget pour afficher la tête du robot
        self.robot_head_label = QLabel(self)
        self.robot_pixmap = QPixmap(resource_path("./img/neutre.png"))  # Assurez-vous que l'image est dans le bon dossier
        self.robot_pixmap = self.robot_pixmap.scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio)  # Réduction de la taille
        self.robot_head_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.robot_head_label.setPixmap(self.robot_pixmap)

        # Layout principal pour inclure uniquement la tête du robot
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.robot_head_label)  # Ajouter la tête du robot au layout

        # Ajouter le menu principal
        self.menu = MainMenu(self.switch_mode)
        self.main_layout.addWidget(self.menu)

        # Créer un widget central pour contenir le layout principal
        self.main_widget = QWidget()
        self.main_widget.setLayout(self.main_layout)
        self.central_widget.addWidget(self.main_widget)


    def switch_mode(self, mode):
        """Passe au mode sélectionné (entraînement, test ou calculatrice)."""
        if mode == "calculator":
            self.game = CalculatorMode(self.switch_back_to_menu)
            self.central_widget.addWidget(self.game)
            self.central_widget.setCurrentWidget(self.game)
        else:
            self.game = RobotGame(mode, self.switch_back_to_menu)
            self.central_widget.addWidget(self.game)
            self.central_widget.setCurrentWidget(self.game)

    def switch_back_to_menu(self):
        """Retourne au menu principal."""
        self.central_widget.setCurrentWidget(self.main_widget)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

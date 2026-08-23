from pathlib import Path

from PySide6.QtCore import QLocale, QSettings, QTranslator
from PySide6.QtWidgets import QApplication


SUPPORTED_LANGUAGES = {
    "de": "Deutsch",
    "en": "English",
    "fr": "Français",
    "it": "Italiano",
    "rm": "Rumantsch",
}

DEFAULT_LANGUAGE = "de"


class TranslationManager:
    def __init__(self, app: QApplication):
        self.app = app
        self.translator = QTranslator()
        self.current_language = DEFAULT_LANGUAGE

        self.translations_dir = (
            Path(__file__).resolve().parent.parent
            / "resources"
            / "translations"
        )

    def load_language(self, language_code: str) -> bool:
        if language_code not in SUPPORTED_LANGUAGES:
            language_code = DEFAULT_LANGUAGE

        self.app.removeTranslator(self.translator)

        if language_code == "de":
            self.translator = QTranslator()
            self.current_language = "de"

            QLocale.setDefault(
                QLocale(
                    QLocale.German,
                    QLocale.Switzerland,
                )
            )

            return True

        translation_file = (
            self.translations_dir
            / f"dfg_{language_code}.qm"
        )

        if not translation_file.exists():
            return False

        new_translator = QTranslator()

        if not new_translator.load(str(translation_file)):
            return False

        self.translator = new_translator
        self.app.installTranslator(self.translator)

        self.current_language = language_code

        locale_map = {
            "en": QLocale(
                QLocale.English,
                QLocale.UnitedKingdom,
            ),
            "fr": QLocale(
                QLocale.French,
                QLocale.Switzerland,
            ),
            "it": QLocale(
                QLocale.Italian,
                QLocale.Switzerland,
            ),
            "rm": QLocale(
                QLocale.Romansh,
                QLocale.Switzerland,
            ),
        }

        QLocale.setDefault(locale_map[language_code])

        return True

    def change_language(self, language_code: str) -> bool:
        if language_code == self.current_language:
            return True

        if not self.load_language(language_code):
            return False

        self.save_language(language_code)

        return True

    @staticmethod
    def get_saved_language() -> str:
        settings = QSettings(
            "DFG Pfannenstiel",
            "DFG-Kursverwaltung",
        )

        language = settings.value(
            "language",
            DEFAULT_LANGUAGE,
            type=str,
        )

        if language not in SUPPORTED_LANGUAGES:
            return DEFAULT_LANGUAGE

        return language

    @staticmethod
    def save_language(language_code: str) -> None:
        if language_code not in SUPPORTED_LANGUAGES:
            return

        settings = QSettings(
            "DFG Pfannenstiel",
            "DFG-Kursverwaltung",
        )

        settings.setValue(
            "language",
            language_code,
        )
# Funkcjonalność 
- Aplikacja umożliwia analizę zdjęć oraz dokumetów .pdf zawierających dowolny tekst
- Za jej pomocą będzie można określić wydźwięk wypowiedzi
- Przetłumaczyć tekst na wybrany język.
- Aplikacja generuje kod dostępu do danej analizy oraz wysyła go na wskazany przez użytkownika adres e-mail.

# Architektura
![picture](https://github.com/matsmolinski/AI-on-Azure-OCR/blob/main/architecture%20azure.svg)

## Opis działania
1. Użytkownik wrzuca zdjęcie/dokument .pdf 
2. Dokument zapisywany jest do Azure Blob Storage
3. Zostaje utworzony rekord w Table Storage oraz nadawany jest kod dostępu do analizy
4. Po zapisaniu pliku uruchamiane jest zdarzenie poprzez Event Grid, które uruchamia Azure Function
5. Azure Function przesyła link do pliku do Cognitive Service Computer Vision / Form Recognizer 
6. Azure Function uruchamia Cognitive Service Translator Text oraz Cognitive Service Text Analytics
7. Wyniki analizy zapisywane są do Table Storage w odpowiednim rekordzie
8. Wysyłana jest wiadomość mail z kodem dostępu
9. Użytkownik wprowadza kod dostępu i wyświetla wyniki analizy

# Stos technologiczny
- Typescript + React
- Azure Cognitive Services API
- Azure Functions
- Azure Blob Storage
- Event Grid
- Azure Table Storage
- Virtual Network

# Harmonogram

# Skład zespołu
 - **Mateusz Smoliński [Lider]**
 - Daniel Sporysz
 - Katarzyna Wolska
 - Konrad Magiera
 - Maciej Kozłowski
 - Rafał Pachnia
 
# Opis projektu

Tworzona przez nas usługa ma służyć do prostej i bezpiecznej analizy plików graficznych i PDF pod kątem wykrywania oraz analizy zawartego tekstu. Analiza zawartego tekstu będzie polegała na ewaluacji wydźwięku tekstu. Aplikacja będzie umożliwiała analizę tekstu w wybranym języku oraz jego tłumaczenie. Usługa będzie dostępna przez serwis webowy. Po wysłaniu pliku do analizy użytkownik otrzyma powiadomienie w aplikacji, że analiza się rozpoczęła oraz, że po zakończeniu dostanie wiadomość email z kodem dostępu do analizy.

# Funkcjonalność 
- Aplikacja umożliwia analizę zdjęć oraz dokumetów .pdf zawierających dowolny tekst.
- Za jej pomocą będzie można:
  - określić wydźwięk wypowiedzi,
  - przetłumaczyć tekst na wybrany język.
- Aplikacja generuje kod dostępu do danej analizy oraz wysyła go na wskazany przez użytkownika adres e-mail.

## Opis działania
![picture](https://github.com/matsmolinski/AI-on-Azure-OCR/blob/main/flow.svg)

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

# Architektura
![picture](https://github.com/matsmolinski/AI-on-Azure-OCR/blob/main/architecture%20azure.svg)

# Instrukcja odtworzenia rozwiązania
1. Utworzyć grupę zasobów, w której będą następujące serwisy: Storage Account, Azure Functions, Logic Apps, Cognitive Services (Translator, Text Analytics, Vision),
2. Utworzenie w Storage Account kontener na blob'y oraz Table Storage,
3. W Azure Functions zaimplementować funkcje zgodnie z kodem źródłowym dostępnym w tym repozytorium kodu,
4. Skonfigurować Logic App:
- uruchamianie za pomocą zapytania http, w któym przekazany będzie adres email oraz kod dostępu do wyników analizy,
- użyć send grid do wysłania maila z kodem na podany adres. 
5. Uzupełnić konfigurację Azure Functions o zmienne używane w funkcjach.


# Harmonogram
26.11.2020 - Wstępna dokumentacja, założenie repozytorium projektu na GitHub  

06.12.2020 - Konsultacja dokumentacji i planu projektu

nb. 07.01.2021 - Middle check-point:
- Skonfigurowany portal Azure
- Upload zdjęcia na Blob
- Tworzenie rekordu w bazie z kodem dostępu
- Podłączenie Event Grid/Logic Apps
- Wykorzystanie Cognitive Services: rozpoznawanie tekstu na zdjęciu, tłumaczenie tekstu, określanie wydźwięku wypowiedzi
- Wysyłanie maila z kodem dostępu

**28.01.2021 - Prezentacja projektu** 
- prototypowe UI
- Stworzenie raportu


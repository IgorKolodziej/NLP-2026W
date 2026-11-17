# Feedback prowadzącej — co faktycznie musimy zmienić?

Prowadząca oceniła proposal na 5,5/10. Największy problem to nie błędy techniczne, lecz niewystarczająco oryginalny wkład badawczy. Pozostałe uwagi dotyczą metodologii, danych i sposobu przedstawienia projektu.

Podzieliłem je na trzy kategorie. W każdej uwagi są uporządkowane od najważniejszych. Rozróżniam też, co rzeczywiście sugeruje prowadząca, a co jest moją propozycją.

Krytyczny

Może zdecydować o wartości naukowej projektu

Wysoki

Wymagane doprecyzowanie lub zmiana

Średni

Ważne, ale nie zmienia głównej koncepcji

Niski

Redakcja lub dodatkowe usprawnienie

## A. Uwagi dotyczące samego projektu

Te kwestie wpływają na hipotezy, eksperymenty, dane lub implementację.

A1. Za mały wkład naukowy

Krytyczny

O co jej chodzi: Samo odtworzenie znanych modeli i dodanie kilku cech nie wystarcza na projekt magisterski. Musicie pokazać, jaką nową wiedzę uzyskacie. Prowadząca wprost pisze, że samo zastępowanie modeli w istniejącym pipeline nie wystarczy.

Rekomendowana zmiana:

- Prowadząca: Sformułować testowalne hipotezy o temporal shift, wprowadzić kontrolowane eksperymenty i systematyczną analizę błędów.
- Moja propozycja: Skoncentrować projekt na tym, które mechanizmy językowe clickbaitu pozostają przydatne przy zmianie czasu i korpusu, a które tracą skuteczność.

Wpływ: hipotezy, eksperymenty i potencjalnie analiza wyników.

A2. Dwanaście cech nie zostało zdefiniowanych

Krytyczny

O co jej chodzi: Piszecie o 12 cechach, ale nie podajecie ich dokładnych definicji. Nie wiadomo więc, czy są oryginalne i jak je wyliczać. Prowadząca zaznacza, że kopiowanie cech z innych prac nie wystarczy na wysoko oceniany wkład.

Rekomendowana zmiana:

- Prowadząca: Wymienić wszystkie 12 cech, podać wzory, reguły i słowniki oraz ustalić je przed uruchomieniem modelu C.
- Moja propozycja: Zaprojektować cechy opisujące konkretne mechanizmy clickbaitu, np. curiosity gap, niedopowiedzenie, bezpośrednie zwroty do czytelnika czy obietnicę zaskoczenia. Nie ograniczać się do długości tekstu i liczby wykrzykników.

Wpływ: feature extractor i eksperymenty ablation.

A3. Ryzyko data leakage

Wysoki

O co jej chodzi: Podobne posty lub artykuły mogą znaleźć się w treningu i teście. Model może wtedy osiągać zawyżone wyniki, które błędnie przypiszemy odporności na temporal shift.

Rekomendowana zmiana:

- Prowadząca: Sprawdzić duplikaty, near-duplicates, daty, dostępne identyfikatory wydawców oraz nakładanie się Webis-16 i Webis-17.
- Moja propozycja: Przygotować jeden powtarzalny protokół wykrywania duplikatów, wykonywany przed każdym eksperymentem.

Wpływ: data preprocessing i tworzenie splitów.

A4. Niedoprecyzowane temporal splits

Wysoki

O co jej chodzi: Zaplanowaliście trening na grudniu, grudniu–styczniu i grudniu–lutym, ale nie pokazaliście liczebności miesięcy. Nie wiadomo, czy każdy test będzie wystarczająco duży.

Rekomendowana zmiana:

- Prowadząca: Podać liczby przykładów i proporcje klas w każdym miesiącu, minimalny rozmiar testu i regułę postępowania, gdy miesiąc jest za mały.
- Moja propozycja: Dodatkowo zmierzyć, czy rzeczywiście występuje zauważalny temporal shift, zanim zaczniemy interpretować różnice F1 jako jego skutek.

Wpływ: EDA, protokół ewaluacji, ewentualnie splity.

A5. Nie wiadomo, co oznacza random grouped split

Wysoki

O co jej chodzi: Piszecie o grupowanym podziale losowym, ale nie definiujecie grup. Nie mogą to być wydawcy, ponieważ nie macie ich identyfikatorów.

Rekomendowana zmiana:

- Prowadząca: Określić klucz grupowania, np. klaster zduplikowanych lub podobnych postów.
- Moja propozycja: Stosować ten sam mechanizm identyfikowania powiązanych przykładów w podziałach losowych i chronologicznych.

Wpływ: split generator.

A6. Niejasna definicja etykiet

Wysoki

O co jej chodzi: Webis-17 zawiera oceny pięciu anotatorów. Nie opisaliście dokładnie, jak z tych ocen powstaje binarne `truthClass` i czy wykorzystacie `truthMean`.

Rekomendowana zmiana:

- Prowadząca: Podać oficjalną regułę mapowania ocen na klasy.
- Moja propozycja: Zachować oficjalne `truthClass` jako etykietę treningową, a zgodność anotatorów wykorzystać w analizie błędów.

Wpływ: głównie dokumentacja danych, ewentualnie analiza błędów.

A7. Kalibracja i wpływ niezbalansowania klas

Średni

O co jej chodzi: Sam macro-F1 nie wystarczy. Trzeba też ocenić jakość przewidywanych prawdopodobieństw oraz metryki zależne od częstości clickbaitów.

Rekomendowana zmiana:

- Prowadząca: Raportować calibration i prevalence-dependent metrics.
- Moja propozycja: Zachować planowane Brier score, reliability diagrams i average precision, a dodatkowo raportować częstość klasy pozytywnej dla każdego testu.

Wpływ: evaluation pipeline. Większość jest już w proposalu.

## B. Uwagi dotyczące tekstu proposalu

To poprawki, które zasadniczo nie wymagają zmiany modeli ani eksperymentów.

B1. Niepoprawne porównanie SOTA

Wysoki

O co jej chodzi: Tabela zawiera 15 prac, ale część wyników nie ma jasno wskazanego splitu, partycji test/dev lub rodzaju F1. Dodatkowo wynik Clickbait Challenge przypisano niewłaściwej publikacji.

Rekomendowana zmiana — prowadząca: Przebudować tabelę, zweryfikować Yu et al. 2024, przypisać wynik zwycięskiego systemu Zhou (2017) i dodać rodzaj uśredniania F1. Dla Michaluk et al. doprecyzować, że wyniki 0,864–0,909 pochodzą z ablation na partycji testowej.

Wpływ: wyłącznie przegląd literatury i tabela SOTA.

B2. Za słabe uzasadnienie temporal shift literaturą

Wysoki

O co jej chodzi: Temporal shift stał się centralnym elementem projektu, ale prawie żadna cytowana praca go nie bada. Nie uzasadniliście też dostatecznie, czym wasze B–C różni się od ablation Michaluk et al.

Rekomendowana zmiana — prowadząca: Dodać literaturę o random splits, temporal adaptation i out-of-domain calibration, szczególnie Søgaard et al. (2021), Röttger & Pierrehumbert (2021) oraz Desai & Durrett (2020).

Wpływ: related work i uzasadnienie hipotez.

B3. Niekompletny opis datasetów

Wysoki

O co jej chodzi: Webis-17 jest opisany dobrze, ale Webis-16 nie ma podanej licencji ani dokładnego źródła. Oficjalny zbiór testowy Webis-17 (18 979 przykładów, etykiety przez TIRA) nie ma statusu `RESTRICTED`.

Rekomendowana zmiana — prowadząca: Uzupełnić licencję i źródło Webis-16, datę pobrania, wersję zbioru i status oficjalnego testu.

Wpływ: opis danych. Weryfikacja faktycznej zawartości Webis-16 to osobne zadanie techniczne.

B4. Zbyt ogólny opis literatury

Średni

O co jej chodzi: Macie 15 publikacji w tabeli, ale wiele nie zostało omówionych w tekście. Czytelnik nie dowiaduje się, co wnoszą do waszego pytania badawczego.

Rekomendowana zmiana — prowadząca: Dodać krótkie omówienie każdej pracy, pokazujące jej związek z projektem.

Wpływ: sekcja SOTA.

B5. Brak rozwinięcia skrótów i DOI

Niski

O co jej chodzi: Skróty takie jak TF-IDF, MSE, ECE, BiGRU, PoC i MR pojawiają się bez wyjaśnienia. Bibliografia nie zawiera DOI.

Rekomendowana zmiana — prowadząca: Rozwinąć skróty przy pierwszym użyciu lub dodać słownik oraz uzupełnić DOI.

Wpływ: redakcja tekstu.

B6. Harmonogram i wkład zespołu są zbyt ogólne

Niski

O co jej chodzi: W harmonogramie kilka zadań ma właściciela „All”, a wpisy o wykonanej pracy są parami niemal identyczne.

Rekomendowana zmiana — prowadząca: Wskazać jedną osobę odpowiedzialną za każdy wspólny etap i podać konkretne rzeczywiście wykonane zadania każdego członka zespołu.

Wpływ: tabele harmonogramu i contributions.

B7. Drobne kwestie formalne

Niski

O co jej chodzi: Usunięto linię informującą o autorstwie szablonu. Warto też doprecyzować, czy split manifests zawierają teksty czy same ID, oraz zachować informacje o wykorzystanych modelach AI i promptach.

Rekomendowana zmiana — prowadząca: Przywrócić atrybucję szablonu i uzupełnić te informacje.

Wpływ: dokumentacja, bez zmiany metody.

## C. Pytania i sugestie — nie są poleceniem przebudowy projektu

Tutaj oddzielam obowiązek udzielenia odpowiedzi od ewentualnego dodatkowego eksperymentu.

C1. Czy nasze wyniki rzeczywiście pokazują temporal shift?

Wysoki

O co jej chodzi: Prowadząca pyta, jakie kontrole duplikatów, dat i wydawców zabezpieczają przed fałszywym efektem zmiany w czasie.

Rekomendowana zmiana:

- Prowadząca: Przedstawić rzeczywiste wyniki audytu.
- Moja propozycja: Dodatkowo porównać rozkłady wybranych cech językowych między miesiącami, aby sprawdzić, czy obserwujemy zmianę danych.

To pytanie wymaga dowodów, nie tylko lepszego sformułowania w raporcie.

C2. Czy można przetestować model na nowszych danych?

Wysoki

O co jej chodzi: Wasze dane pochodzą z lat 2016–2017. Wyniki nie pokazują, jak model poradziłby sobie z clickbaitami publikowanymi obecnie.

Rekomendowana zmiana:

- Prowadząca: Wskazać, jaki późniejszy korpus jest dostępny do takiej ewaluacji.
- Moja propozycja: Zrobić przegląd nowszych datasetów i sprawdzić zgodność definicji clickbaitu. Dodać eksperyment tylko wtedy, gdy dane są odpowiednie.

Ważne: Webis-16 tego pytania nie rozwiązuje, ponieważ jest starszy od Webis-17.

C3. Dlaczego nie badamy nowych wydawców?

Średni

O co jej chodzi: Pierwotny temat zakładał publisher-held-out evaluation. Wasz Webis-17 nie ma jednak identyfikatorów wydawców.

Rekomendowana zmiana — prowadząca: Wyjaśnić ograniczenie i konsekwencję braku publisher IDs. Prowadząca już zaakceptowała przejście na dozwolony wariant time-held-out.

Nie trzeba zmieniać całego protokołu ani sztucznie odtwarzać wydawców.

C4. Czy możemy stworzyć uniwersalny protokół audytu leakage?

Niski

O co jej chodzi: Prowadząca sugeruje, że powtarzalna procedura kontroli duplikatów i przecieków mogłaby być dodatkowym wkładem badawczym.

Rekomendowana zmiana:

- Prowadząca: Zebrać dodatkowe dowody i rozważyć przenośny protokół.
- Moja propozycja: Nie robić z tego osobnego celu naukowego, chyba że analiza danych pokaże istotny problem.

To rozszerzenie opcjonalne.

## Podsumowanie: co jest najważniejsze?

## 5 rzeczy, na których skupiłbym się najpierw

1. Wkład naukowy: określić, co nowego badamy, a nie tylko jakie modele porównujemy.
2. 12 cech: opracować ich dokładne, uzasadnione i możliwie oryginalne definicje.
3. Temporal shift: sprawdzić, czy nasze dane pozwalają rzeczywiście badać zmianę w czasie.
4. Data leakage: upewnić się, że podobne przykłady nie fałszują wyników.
5. SOTA: poprawić tabelę i uzasadnienie metodologii wcześniejszymi badaniami.

### Czy trzeba przebudować obecny projekt?

| Obszar              | Wstępna decyzja                     |
| ------------------- | ----------------------------------- |
| Modele A i B        | Raczej bez zmian                    |
| Model C             | Nowa, precyzyjna specyfikacja cech  |
| Główna hipoteza     | Wymaga wzmocnienia                  |
| Temporal evaluation | Zachować, ale zweryfikować          |
| Cross-corpus        | Zachować jako dodatkowy eksperyment |
| Data preprocessing  | Rozszerzyć kontrole                 |
| Metryki             | Głównie realizacja obecnego planu   |
| Proposal            | Istotne poprawki                    |

Mój wniosek: feedback nie wymaga rewolucji w architekturze. Wymaga natomiast znaczącego wzmocnienia metodologii. Największym błędem byłoby teraz poświęcić czas na Qwena czy LoRA, zanim ustalimy, co dokładnie chcemy wykazać naszymi 12 cechami i eksperymentami temporalnymi.




### Uzupełnienie: szczegóły techniczne i formalne z feedbacku

Warto mieć je na uwadze przy projektowaniu cech i poprawie tekstu, żeby nie uciekły w trakcie prac:

* **Konkretne brakujące cechy (do A2):** Prowadząca wprost wytknęła, że karta tematu wymienia **liczebniki (*numerals*)** oraz **stopień najwyższy (*superlatives*)**, a żadna z tych rodzin cech nie pojawiła się w naszej propozycji.


* **Różnica między naszym B vs C a pracą Michaluk et al. (do B2):** W wyjaśnieniu, czym nasze kontrolowane porównanie różni się od ich ablation na XGBoost, musimy wprost wskazać, że w tamtej pracy zmieniała się również **szerokość embeddingów (*embedding width*)**.


* **Brak metryki *per-publisher F1* (do C3):** Oprócz samego wyjaśnienia braku ID wydawców, musimy wprost napisać w raporcie, że z tego powodu nie raportujemy wymaganej w karcie metryki *per-publisher F1*.


* **Zobowiązanie do analizy błędów (do A1):** Karta wymaga analizy minimum 12 błędów – my zadeklarowaliśmy **20 błędów** i tego progu musimy się trzymać.


* **Drobne wymogi formalne (do B6 i B7):**
* **Tabela 3** (harmonogram tygodniowy) nie jest ani razu przywołana w treści tekstu – trzeba dodać do niej odwołanie.


* Przy deklaracji użycia narzędzi AI (ChatGPT, Perplexity) należy dopisać **konkretne wersje modeli** (oprócz zachowania promptów).

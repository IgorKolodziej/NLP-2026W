
### Liczność wg miesiąca (cały zbiór)

| Miesiąc | N | Clickbait | % cb |
|---------|---|-----------|------|
| 2016-12 | 3832 | 1012 | 26.4% |
| 2017-01 | 3848 | 884 | 23.0% |
| 2017-02 | 3504 | 814 | 23.2% |
| 2017-03 | 3918 | 908 | 23.2% |
| 2017-04 | 3580 | 830 | 23.2% |

**5 miesięcy**, suma **18 682**, globalnie **23.8%** pozytywów.

### Split `temporal_main` (train Dec–Jan–Feb / val Mar / test Apr)

| Part | N | Miesiące |
|------|---|----------|
| **train** | 11 184 | 3832 + 3848 + 3504 |
| **val** | 3 918 | tylko 2017-03 |
| **test** | 3 580 | tylko 2017-04 |



Temporal (główny protokół + 2 warianty „okien”)
Nazwa	Train	Val	Test
temporal_w1_dec_jan_feb
2016-12 (3832)
2017-01 (3848)
2017-02 (3504)
temporal_w2_decjan_feb_mar
2016-12+01 (7680)
2017-02 (3504)
2017-03 (3918)
temporal_main
2016-12–02 (11 184)
2017-03 (3918)
2017-04 (3580)




Czym jest „grouped”?
Jednostką podziału nie jest pojedynczy post, lecz article_group_key (znormalizowany targetTitle, albo id gdy brak tytułu). Cała grupa trafia do jednego z train/val/test — żeby ten sam artykuł (ten sam tytuł) nie wyciekał między partycjami. Losowanie jest osobno dla grup clickbait vs nie-clickbait (stratyfikacja po etykiecie na poziomie grupy). To split diagnostyczny (łatwiejszy, i.i.d.), nie główna metryka temporalna.

Po czyszczeniu (jeden post na article_group_key) praktycznie 1 wiersz = 1 grupa (~18 682 grup), więc liczby są bliskie losowemu mieszaniu postów — ale reguła grupowania zostaje na wypadek overlapu artykułów.
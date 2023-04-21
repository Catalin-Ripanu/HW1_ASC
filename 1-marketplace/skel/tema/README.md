Nume: Cătălin-Alexandru Rîpanu
Grupa: 333CC

# Tema 1 - ASC

### Organizare
Tema 1 se referă la implementarea unui *Marketplace* care reprezintă obiectul
central modelării problemei _Multiple Producers - Multiple Consumers_ în care
fiecare producător își oferă produsele spre vânzare, iar fiecare consumator
achiziționează produsele puse la dispoziție, cu mențiunea că un anumit
consumator poate deveni un producător dacă elimină un produs din coșul
său de cumpărături.

Consider că implementarea aleasă este una optimă și naturală din punct de vedere
al utilizării multiplelor fire de execuție care accesează resurse partajate. De
asemenea, tema și-a dovedit utilitatea având în vedere faptul că abordează o
problemă a unui domeniu vast, de interes, și anume Calculul Paralel, respectiv
Multithreading.

### Implementare
*Clasa Consumer* reprezintă modelarea thread-ului consumator care, pe baza unui
ID al unui coș construit sub forma unei liste, poate scoate sau adăuga produse
folosind un dicționar ce conține _funcții_. Atunci când toate operațiile se
îndeplinesc, consumatorul apelează funcția *place_order()* pentru a își goli coșul
de cumpărături. În situația în care operația curentă eșuează, consumatorul
așteaptă un timp ce este extras din fișierul de intrare. Evident, execuția acestui
tip de thread se incheie atunci când se activează comanda produselor.

*Clasa Producer* reprezintă modelarea thread-ului producător care publică, prin
intermediul Marketplace-ului, produse destinate consumatorilor. Un astfel de
thread primește o listă de produse pe care o iterează la infinit astfel încât
toți consumatorii să obțină produsele dorite. Dacă operația de publicare se
îndeplinește cu succes, producătorul așteaptă un timp ce este extras din propria 
listă de produse. În caz contrar, așteaptă un timp ce este dat thread-ului la
creare.

*Clasa Marketplace* reprezintă punctul central al implementării întrucât oferă
metode ce sunt apelate atât de consumatori, cât și de producători, cu alte
cuvinte, joacă rolul unei *fațade* ce facilitează sincronizarea și comunicarea
acestor thread-uri. Această clasă reține o *listă de produse* disponibile, un
dicționar care asociază un anumit ID cu o anumită listă de produse dintr-un
coș de cumpărături și un alt dicționar care mapează un produs cu producătorul
său ce va fi folosit atunci când un consumator decide să renunțe la produsul
pus în coșul său.

Pentru a ține evidența numărului maxim de produse ce se pot publica de către
un producător, se folosește un dicționar care leagă ID-ul unui astfel de thread
de capacitatea cozii sale de produse (această capacitate se modifică în cadrul
funcțiilor *publish()*, *add_to_cart()* și *remove_from_cart()*).

Evident, toate operațiile care nu sunt thread-safe, cum ar fi incrementările sau
decrementările, sunt protejate folosind mecanisme de sincronizare specializate,
mai exact *Lock-urile*.

Atunci când se efectuează o comandă, toate produsele din coșul respectiv sunt
afișate la stream-ul de output înainte ca lista care modelează coșul să fie 
returnată consumatorului.

### Resurse Utilizate
[1]: https://ocw.cs.pub.ro/courses/asc/laboratoare/01
[2]: https://ocw.cs.pub.ro/courses/asc/laboratoare/02
[3]: https://docs.python.org/3/library/logging.html
[4]: https://docs.python.org/3/library/logging.handlers.html#logging.handlers.RotatingFileHandler
[5]: https://docs.python.org/3/howto/logging.html

### Git
[1]: https://github.com/CatalinACS/Tema1-ASC

### Link Drive ce conține .git-ul
[1]:

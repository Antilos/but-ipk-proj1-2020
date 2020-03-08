# Http Resolver Doménových mien
Server prijíma http správy GET a POST a zaisťuje preklad doménových mien

## Implementácia
Pre implementáciu bol zvolený jazyk Python. Server aj preklad doménových mien bol implementovaný pomocou balíka _socket_. Transportnou službou je TCP, spojenie je neperzistentné.

## Použitie
Server po spustení beží nepretržite, a príjma správy na konkrétnej ip adrese a konkrétnom porte (obe zvolené pri spustení). Po prijatí správy vykoná server preklad doménového mena, a zašle klientovi http odpoveď s prekladom, respektíve s príslušným chybovým kódom. V hlavičke odpovede sa naviac nachádza čas odpovede. Spojenie je potom ukončené.

Server je možné ukončiť pomocou klávesového prerušenia.
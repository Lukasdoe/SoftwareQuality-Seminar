# Aggregierte Daten

#Betrachtete Repositories: 100
#Betrachtete Commits: 100

## Dependency Injection Frameworks

#`pom.xml`-Files, die ... als Abhängigkeit angeben (in letztem Commit auf master (`latest_commit_hash`)):

 * Spring Framework: 53
 * Guice: 17
 * Dagger: 3
 * CDI: 5

## Unsafety

Aussagen über Vorkommen von Codefragmenten sind immer accumuliert über die 100 betrachteten Commits. Also sind die Aussagen über Code, der irgendwann mal existiert hat, zwischen den 100 Commits. 

### Configfiles

Nummer von Gesamtcommits vs Nummer von Config Files Changes: 
 => Gesamt: 10.000 (Gesamtcommits) vs 989 (Commits die Configfiles ändern)

Durchschnittliche Nummer an Zeilen geändert pro Commit der Config File ändert: 1971657 / 989 = 1993.586
Durchschnittliche Nummer an geänderten Files pro Commit (gesamt): 11721 / 10.000 = 1,1721
Durchschnittliche Nummer an geänderten Files pro Commit (der auch min. 1 geändert hat): 11721 / 989
Total number of changed files (sum): 11721
Total number of changed lines: 1971657

### Dependency Injection

#### Spring

#Commits die eine @Bean oder @Component hinzufügen / entfernen: 124
Gesamtzahl der Beanänderungen (@Bean oder @Component): 484
#Repos die Spring als Dependency haben: 53

#### Guice

#Repos die Guice als Dependency haben: 17
#Repos mit Netflix Governator: 0

Vorkommen in Changes:
* `bind(...)`: 128
* Provide-Annotations: 
  * `@Provides`: 103
  * `@ProvidesIntoSet`: 18
  * `@ProvidesIntoMap`: 15
* Gesamt: 297

Kein Governator -> kein `LifecycleInjector`

### Profiling problems / incompatibilities

1. Wie viele Projekte benutzen Code der nicht mit ... funktioniert:
    * Ekstazi: 11
    * Openclover: 49
    * Openclover und Ekstazi: 3
    -> Gesamt: 63

2. Gesamtfiles die inkompatibel sind: 932 (= 932/63 = 14.8 Files pro Projekt)

### Reflections

* Projekte, die mindestens einmal `Class.forName` reflections benutzen: 56
* Gesamtvorkommen von `Class.forName`: 333
* Projekt mit den meisten `Class.forName`: 36  quarkusio/quarkus
* Projekt mit den wenigsten, aber > 0: 1 apache/incubator-shenyu

Sehr fehlerbehaftet, daher bitte Vorsicht hier:
* #Commits die eine Klasse ändern, die per Reflection accessed wird (gesamt): 72
* #Repos wo ich das tracken konnte: 8
-> kann meistens nicht einfach getracked werden, da die Klasse, die reflexiv angesprochen wird, oft erst dynamisch ermittelt wird.

## Gesamtstatistik

Diese soll lauten: "Jeder Commit unter den untersuchten Commits hat im Schnitt ..."
 * 11721 / 10000 = 1,1721 Configuration Files geändert
 * 484 / 10000 = 0,0484 Beans geändert
-> Die anderen Änderungen sind nicht gut auf Commits zurück zu führen

Von 100 untersuchten Projekten haben 88 in den 100 untersuchten Commits mindestens 1 Art von unsafety. 
8 Projekte beinhalten in den untersuchten Commits sogar jede Art von entdeckter Unsafety.

## Limits der Scans:

- Es wird nicht zwischen auskommentiertem und aktivem Code unterschieden
- Eine false-positives sind möglich, dadurch entweder zu liberal gematcht wurde oder außerhalb von .java source files gesucht wurde (injection_scanner)
- Es konnte nur plaintext source code untersucht werden -> .jar Files und andere nicht-plaintext formate wurden ignoriert

# Proof Of Concept Repositories

Maven Module die als Demonstratoren für Quellen von "Unsafety" bei Regression Test Selection (RTS) dienen. Jedes Modul kann als einzelnes Java Projekt betrachtet werden, wobei dieses Eltern- / Rootprojekt hier zum Bereitstellen einer gemeinsamen Konfiguration dient.

___

## Voreinstellungen

Durch den enthaltenen `pom.xml` File sind bereits alle notwendigen Einstellungen vorgenommen:

Versionen der untersuchten RTS Tools:

   - Ekstazi 5.3.0
   - STARTS 1.4-SNAPSHOT (Compiled aus [GitHub Repository Master Branch](https://github.com/TestingResearchIllinois/starts), Commit `e1d29be2958ec27fac12e6c8611577fce5a73e40`)
   - HyRTS 1.0.1
   - OpenClover 4.4.1
   - GIBstazi 3.5.7

Kompatibilität der Tools mit verschiedenen JUnit Versionen:

| Tool     | JUnit3 | JUnit4 | JUnit5 |
|----------|--------|--------|--------|
| STARTS   |   +    |    +   |   +    |
| EKSTAZI  |   +    |    +   |   x    | -> Erkennt Tests nicht / lässt sie immer laufen
| GIBstazi |   +    |    +   |   x    | 
| HyRTS    |   +    |    nur bis 4.10 (4.12)   |   x    | -> failed manchmal bei Juni4 mit einem Stackoverflow error
| Clover   |   +    |    +   |   +    |

Ein `+` bedeutet hier, dass ein Test des Tools ergeben hat, dass es mit der Version umgehen kann. Ein `x` bedeutet das Gegenteil. `HyRTS` funktioniert entgegen Angaben aus der Dokumentation nicht mit allen JUnit Versionen >= 4.10. Da jedoch Version 4.10 funktioniert, wurde diese als niedrigster Standard für alle hier enthaltenen Tests gewählt. Alleine die Dependency Injection Tests basieren auf Funktionalität des Spring Frameworks, die erst ab JUnit Version 4.12 lauffähig sind. Daher wurde für diese Tests als Ausnahme JUnit 4.12 gewählt, was auch in Kombination mit HyRTS funktioniert.

Die Java Version des gesamten Projektes ist Version `Java-SE 1.8.0-291 (Version 8)`, da dies die höchste Version der Programmiersprache ist, die von allen Tools unterstützt wird und weiterhin unterstützt ist.

Zur Java Versionsverwaltung wird [jabba](https://github.com/shyiko/jabba) genutzt.

Weitere Versionen:
 - Maven: 3.8.3
 - Maven Surefire Plugin: 3.0.0-M5

# Benutzung

Jedes RTS Tool, sowie die JUnit Versionen 3, 4.10, 4.12 und 5 können über entsprechende [Maven Profile](https://maven.apache.org/guides/introduction/introduction-to-profiles.html) aktiviert werden.

Wichtig: Das Projekt ist so strukturiert, dass immer nur einzelne Maven Module verwendet werden sollen, daher müssen die folgenden Befehle immer in dem Modulordner ausgeführt werden, dessen Tests ausgeführt werden sollen.

Die Tools "Ekstazi", "GIBstazi" und "OpenClover" werden nach Aktivierung durch den das normale `test`-Goal aktiviert, hier kann also einfach der folgende Befehl verwendet werden:

```bash
mvn test -P JUnit4.10, (EKSTAZI | GIBstazi | OpenClover)
```

Das Tool "STARTS" definiert ein eigenes Maven Goal und wird nicht über das normale `test`-Goal ausgeführt:

```bash
mvn edu.illinois:starts-maven-plugin:starts -P JUnit4.10
```

Auch "HyRTS" hat sein eigenes Goal. Außerdem muss hier noch der JVM Parameter `-Djdk.attach.allowAttachSelf=true` übergeben werden, z.B. über die `MAVEN_OPTS`-Umgebungsvariable.

```bash
export MAVEN_OPTS="-Djdk.attach.allowAttachSelf=true"
mvn org.hyrts:hyrts-maven-plugin:HyRTS
```

Um alle (v.a. von den RTS Tools) generierten Files zu löschen, kann das `clean`-Goal ausgeführt werden. (auch global möglich)

```bash
mvn clean
```
___

## Unsicherheiten und Nachgestellte Szenarien

|ID|Ausgangssituation|Änderung|Modul|
|-|-|-|-|
|0|Programmverhalten basiert auf Inhalt einer externen Ressource|Der Inhalt der externen Ressource wird geändert|`ConfigurationFiles`|
|1|Eine Klasse besitzt eine statische Initialisierung mit Seiteneffekten. Diese Initialisierung wird jedoch nicht ausgeführt, da die Klasse nicht durch den ClassLoader geladen / initialisiert wird.|Die Klasse wird nun durch den Classloader geladen / initialisiert. (kein Objekt erzeugt)|`ClassLoaderMonitoring`|
|2|Eine Klasse `Child` erbt Funktionalität von einer Superklasse `Parent`. Eine Methode `m` ist nur in der Klasse `Parent` definiert. Ein Test ruft die Methode `Child.m()` auf.|Nun implementiert das Kind die Methode `m` mit einer anderen Funktionalität.|`DynamicDispatch`|
|3|Die Eigenschaften einer Klasse werden über Methoden ihrer `Class` Metaklasseninstanz abgefragt.|keine, Tools erzeugen durch Laufzeitinstrumentalisierung die Probleme.|`ProfilingProblems`|
|4|Auf eine Klasse wird durch ihre Meta-Klasseninstanz der Klasse `Class` zugegriffen. Diese Instanz wurde durch einen Aufruf von `Class.forName(...)` erzeugt.|Es werden Änderungen an der Klasse vorgenommen.|`Reflections`|
|5|\*Dependency Injection mittels Spring Framework: Hauptapplikation: `@SpringBootApplication`, enthält `@EnableAutoConfiguration`. Bean in einer `@Configuration` Klasse gegeben.|Neue Bean in neuer `@Configuration` Klasse deklariert, die die alte Bean z.B. mit `@Primary` ersetzt.|`DependencyInjectionSBC`|
|6|\*Dependency Injection mittels Spring Framework: Keine `@SpringBootApplication`, keine `@EnableAutoConfiguration`. Bean in einer `@Configuration` Klasse 1 gegeben. Fully Qualified Name des Moduls der Konfigurationsklasse 1 als `@ComponentScan` Attribut einer `@Configuration` Klasse 2 gegeben.)|Es wird eine weitere `@Configuration` Klasse 3 im selben Modul wie Klasse 1 angelegt. Die ursprüngliche Bean wird (z.B. durch `@Primary`) ersetzt.|`DependencyInjectionComponentScan`|
|7|\*Dependency Injection mittels Spring Framework: Beans gleichen Typs in einer `@Configuration` Klasse gegeben. Beans werden als Collection (z.B. `List`) injected|Neue Bean in neuer `@Configuration` Klasse deklariert, keine zusätzliche Priorisierung nötig.|`CollectionInjection`|
|8|Eine Bibliothek wird durch den `pom.xml`-File als Abhängigkeit mit einer Version festgelegt. Getesteter Code bzw. ein Test benutzt eine Funktionalität dieser Bibliothek.|Die Bibliotheksversion wird in dem `pom.xml` auf eine Version geändert, die nicht mehr auf die selbe Weise funktioniert.|`DependencyConfigFiles`|
|9|\*Eine Abhängigkeit wird als Bean mittels Spring Dependency Injection in der Anwendung verwendet.|Die Abhängigkeit wird geändert.|`DependencyInjectionSource`|
|10|Eine Abhängigkeit wird durch einen Guice `Injector` injected.|Die Implementierung der Abhängigkeit wird geändert.|`DependencyInjectionSourceGuice`|
|11|*Eine Abhängigkeit wird mittels Guice Dependency Injection verwendet.|In das Modul, in der die Abhängigkeit definiert wird, wird eine der `@Provides`-Annotationen hinzugefügt. (z.B. `@Provides` oder `@ProvidesIntoSet`)|`DependencyInjectionGuiceProvides`| 

|ID|Ekstazi|GIBstazi|OpenClover|STARTS|HyRTS|
|:-:|:-:|:-:|:-:|:-:|:-:|
|0|❌|✅|❌|❌|❌|
|1|❌|❌|❌|❌|❌|
|2|✅|✅|❌|✅|✅|
|3|❌|❌|❌|✅|✅|
|4|✅|✅|✅|❌|❌|
|5|❌|⚠️\*\*|⚠️\*\*\*|❌|❌|
|6|❌|❌|❌|❌|❌|
|7|❌|⚠️\*\*|⚠️\*\*\*|❌|❌|
|8|❌|✅|❌|✅|❌|
|9|✅|⚠️\*\*|⚠️\*\*\*|❌|✅|
|10|✅\*\*\*\*|✅\*\*\*\*|✅|❌|✅|
|11|✅\*\*\*\*|✅\*\*\*\*|✅|✅|❌|

* \*: Unsafety wurde aufgrund von Tipps / vorhandener Arbeit von Daniel Elsner und Simon Hundsdorfer gefunden.
* \*\*: Da die von GIBstazi verwendete Ekstazi Version die Methode `Class.getTypeName(...)` nicht unterstützt, kann GIBstazi den `SpringRunner` nicht ausführen.
* \*\*\*: OpenClover erkennt Tests des SpringRunners hier nicht.
* \*\*\*\*: Ekstazi kann diese Tests mit der neusten Version von Guice nicht ausführen. Daher muss
  hier Version 4.2.3 verwendet werden, da sonst die Methode `getAnnotatedSuperclass(...)` nicht unterstützt wird.

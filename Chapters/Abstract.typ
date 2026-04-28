#let abstract_content = [

  This study examines how different Python runtimes affect the performance of the @sw:long local sequence alignment algorithm. A synthetic benchmark was used to compare the standard CPython interpreter, the experimental CPython 3.14 @jit:short compiler, PyPy, and a Cython-based implementation across synthetic sequence scenarios and problem sizes from 100 to 10,000 characters.

  The results show clear performance differences between the tested runtimes. PyPy consistently achieved the best runtime and throughput. Cython also improved on the CPython baseline, and the CPython 3.14 @jit:short compiler showed modest but measurable gains. The study therefore demonstrates that the choice of the right runtime can dramatically accelerate computationally intensive algorithms in bioinformatics without having to leave the Python ecosystem.

  #heading([Abstrakt], numbering: none)

  Diese Arbeit untersucht, wie sich verschiedene Python-Runtimes auf die Performance des Smith-Waterman-Algorithmus auswirken. Dabei wurde ein synthetisches Benchmark verwendet, das den Standard-CPython-Interpreter, den experimentellen CPython-3.14-JIT-Compiler, PyPy und eine Cython-basierte Implementierung anhand synthetischer Sequenzszenarien und Problemgrößen von 100 bis 10.000 Zeichen vergleicht.

  Die Ergebnisse zeigen deutliche Performance-Unterschiede zwischen den getesteten Runtimes. PyPy zeigte durchgehend die beste Laufzeit und den höchsten Durchsatz. Cython verbesserte die Performance gegenüber der CPython-Basis ebenfalls, während der CPython-3.14-JIT-Compiler kleine, aber messbare Zugewinne zeigte. Insgesamt zeigt die Studie, dass bereits die Wahl der Runtime rechenintensive bioinformatische Algorithmen deutlich beschleunigen kann, ohne das Python-Ökosystem verlassen zu müssen.
]

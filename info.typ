#let common_info = (
  thesis_title: "Performance of Different Python Runtimes for a Bioinformatics Algorithm",
  thesis_subtitle: "Testing the Smith-Waterman algorithm across CPython, PyPy, and Python 3.14's native JIT",
  author_name: "Rubin Chempananickal James",
  author_email: "rubin.chempananickal-james@stud-provadis-hochschule.de",
  matriculation_number: "D876",
  university_name: "Provadis School of International Management and Technology",
  department_name: "Information Technology",
  module_name: "Fortgeschrittene Programmierung",
  reviewer_name: "Prof. Dr. Henrik Paul",
  submission_date: datetime.today(),
)

#let wab_info = (
  common_info
    + (
      document_type: "WAB",
    )
)

#let exposee_info = (
  common_info
    + (
      document_type: "WAB Exposé",
    )
)

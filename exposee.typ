#import "info.typ": exposee_info
#import "template.typ": abbreviation_table, glossary_table, numbered_section, paper, title_page, unnumbered_section
#import "Chapters/Glossary.typ": abbreviation_entries, glossary_entries
#import "Chapters/Exposee.typ": exposee_content

#show: paper

#set page(numbering: "I")
#counter(page).update(1)

#title_page(exposee_info)

#numbered_section([
  #outline(title: [Contents])
])

#unnumbered_section([Glossary], glossary_table(glossary_entries))

#unnumbered_section([Abbreviations], abbreviation_table(abbreviation_entries))

#set page(numbering: "1")
#counter(page).update(1)

#unnumbered_section([Exposé], exposee_content)

#set page(numbering: "i")
#counter(page).update(1)

#numbered_section([
  #bibliography("references.bib", title: [References], full: true)
])

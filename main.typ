#import "info.typ": wab_info
#import "template.typ": paper, title_page, unnumbered_section, numbered_section, glossary_table, abbreviation_table, ai_declaration_table, declaration_text
#import "Chapters/Glossary.typ": glossary_entries, abbreviation_entries
#import "Chapters/Abstract.typ": abstract_content
#import "Chapters/01_Introduction.typ": introduction_content
#import "Chapters/02_Methods.typ": methods_content
#import "Chapters/AI_Declaration.typ": ai_declaration_intro, ai_declaration_entries

#show: paper

#set page(numbering: "I")
#counter(page).update(1)

#title_page(wab_info)

#unnumbered_section([Abstract], abstract_content)

#numbered_section([
	#outline(title: [Contents])
])

#unnumbered_section([Glossary], glossary_table(glossary_entries))

#unnumbered_section([Abbreviations], abbreviation_table(abbreviation_entries))

#set page(numbering: "1")
#counter(page).update(1)

#numbered_section(introduction_content)

#numbered_section(methods_content)

#pagebreak()
#set page(numbering: "i")
#counter(page).update(1)

#numbered_section([
	#bibliography("references.bib", title: [References], full: true)
])

#unnumbered_section([AI Declaration], [
	#ai_declaration_intro

	#v(0.8cm)
	#ai_declaration_table(ai_declaration_entries)
])

#unnumbered_section([Declaration of Authorship], declaration_text(wab_info))
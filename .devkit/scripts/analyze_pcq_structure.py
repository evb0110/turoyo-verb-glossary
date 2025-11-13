#!/usr/bin/env python3
"""
DEEP ANALYSIS: What is the actual structure of the pčq etymology?
"""

text1 = "pčq (< prčq cf. Kurd. p'erçiqandin vt. (-p'erçiq-). 1) to crush,"
next1 = "press, smash, squash, KED 107)"

print("=" * 80)
print("STRUCTURE ANALYSIS: pčq etymology")
print("=" * 80)

print("\n📝 PARAGRAPH 1:")
print(f"   {repr(text1)}")

print("\n📝 PARAGRAPH 2:")
print(f"   {repr(next1)}")

print("\n🔍 EXPECTED FULL ETYMOLOGY:")
print("   'prčq cf. Kurd. p'erçiqandin vt. (-p'erçiq-). 1) to crush, press, smash, squash, KED 107'")

print("\n💡 KEY OBSERVATION:")
print("   The etymology in para 1 is: (< ... )")
print("   But there's text AFTER the closing paren: ' to crush,'")
print("   And para 2 ALSO ends with ')'")

print("\n🤔 TWO POSSIBLE INTERPRETATIONS:")

print("\n   Interpretation A: Single etymology with formatting error")
print("   - Etymology: 'prčq cf. Kurd. p'erçiqandin vt. (-p'erçiq-). 1) to crush, press, smash, squash, KED 107'")
print("   - The ')' after '1' is part of the list item '1)', not closing paren")
print("   - The final ')' in para 2 closes the etymology")

print("\n   Interpretation B: Etymology + additional meaning")
print("   - Etymology: 'prčq cf. Kurd. p'erçiqandin vt. (-p'erçiq-). 1'")
print("   - Additional text: ') to crush, press, smash, squash, KED 107'")

print("\n🔬 Let me check if the ')' after '1' is really a closing paren...")

# Find all parentheses
parens = []
for i, char in enumerate(text1):
    if char in '()':
        parens.append((i, char))

print("\n   Parentheses in para 1:")
for pos, char in parens:
    context = text1[max(0,pos-5):pos+6]
    print(f"      pos {pos:2d}: '{char}' in context: {repr(context)}")

print("\n   Nesting structure:")
depth = 0
for pos, char in parens:
    if char == '(':
        context = text1[pos:pos+15]
        print(f"      {' ' * depth}( at {pos:2d}: {repr(context)}")
        depth += 1
    else:
        depth -= 1
        context = text1[max(0, pos-10):pos+1]
        print(f"      {' ' * depth}) at {pos:2d}: {repr(context)}")

print("\n🎯 VERDICT:")
print("   If depth=0 at position 53, then ')' after '1' DOES close the etymology!")
print("   The text 'to crush,' is OUTSIDE the etymology parentheses")
print("   But this doesn't make sense semantically - '1) to crush' is part of the meaning!")

print("\n💡 ACTUAL ISSUE:")
print("   The DOCX has malformed parentheses!")
print("   It should be: pčq (< prčq cf. Kurd. p'erçiqandin vt. (-p'erçiq-) 1) to crush, press, smash, squash, KED 107)")
print("                      ^                                            ^                                        ^")
print("                      open                                         close nested                           close main")
print("   But it is:    pčq (< prčq cf. Kurd. p'erçiqandin vt. (-p'erçiq-). 1) to crush,")
print("                      ^                                            ^  ^")
print("                      open                                         close nested  close main (WRONG!)")

print("\n✨ SOLUTION:")
print("   The parser needs to detect when text continues after a seemingly-closed etymology.")
print("   Heuristic: If the last char in para 1 is ',' and next para ends with ')', ")
print("   then the etymology likely spans both paragraphs despite balanced parens.")

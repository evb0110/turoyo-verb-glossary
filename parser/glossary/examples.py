"""Split boxes into source-order examples, without changing the source text."""

import re

from .docx import Text, join

NUMBER = re.compile(r"(?<![\w/:.])(\d{1,2})\)(?=\s|[^\W\d_]|[‘ʻ\"(\[]|$)\s*")
PREFIX = r"(?:prs|PrS|JL|Jl|LB|MM|LuF|EL|RT|DD|QM|HD|Lehrbuch|jastr|lj|XB|YT|SZ|IA)\.?"
LOCATION = r"(?:[IVX]+\.)?\d+(?:[./]\d+)*(?:\s*[-–,]\s*\d+(?:[./]\d+)*)*"
# Recording labels are tokens from their first character, including numeric
# prefixes, spaces in titles, and optional line/timestamp locators.
RECORDING = r"(?:\d[\w.-]*_|NE_|tru_IL_conj_|Malfono_|Aḥmad_)[\w.-]*(?:[ \w.-]*?)(?:[;,:]\s*\d+(?::\s*\d+)?|;?(?=[ \t]*(?:[’ʼ')]|\n|$)))"
NAME = r"(?-i:[A-ZİḤŠʕʔ][^\W\d_]*)(?:[-/][^\W\d_]+)*"
PERSON = rf"{NAME}(?:[ ]{NAME}){{0,2}}"
DATE = r"(?:\d{1,4}\s*[./_–-]\s*\d{1,2}\s*[./_–-]\s*\d{1,4}|[A-Z][a-z]+\s+\d{1,2},?\s+\d{4})"
REF = re.compile(
    rf"(?P<prefixed>{PREFIX}\s*{LOCATION})"
    r"|(?P<tag>\[(?:MT|LTN|ML|FKD|SL|ST)\]|(?-i:ST|IT|BS|SB|RBP)\b)"
    rf"|(?P<source>{RECORDING}|Xori[- ]Caziz[^;\n]*|NE_Ezo_Koviye\b"
    r"|Maḥkay Ḥḏo Ḥreto \d+ \d+:\d+|Shabo\b|Jan\(\)|Isḥaq Old houses:\d+)"
    r"|(?P<corpus>(?:(?-i:[A-Z])[\w.-]*_[\w.-]+|NE|SZ|Jan|IA|Hanna Dewo)\s*\d*[;/]\d+)"
    r"|(?P<context>\([^()\n]*(?:\d+[:.]\s*\d+|_\w+|\b(?:HD|NE|FG|Xori[- ]Caziz)\b)[^()\n]*\))"
    r"|(?P<text>\d{1,3}/\d{1,4}(?:\s*[-–,]\s*\d+(?![\d/]))*)"
    r"|(?P<page>\d{1,4}(?:\s*[-–]\s*\d+)?)"
    rf"|(?P<pc>(?:\([^()\n]*\bp\.?c\.?[^()\n]*\)?|p\.?c\.?\s+{PERSON}(?:\(\))?|{PERSON}\s+p\.?c\.?)"
    rf"(?:\s+{DATE})?)",
    re.IGNORECASE,
)
OPEN = "ʻ‘ʽ„“\"'"
CLOSE = "ʼ’ʾ”\"'"
PAIRS = {"ʻ": "ʼ", "‘": "’", "ʽ": "ʼ", "„": "“", "“": "”", '"': '"', "'": "'"}


def closing_quote(text, begin, italic=()):
    stack = [PAIRS[text[begin]]]
    for i in range(begin + 1, len(text)):
        char = text[i]
        # Plural possessives inside English glosses are not closing marks.
        following = re.match(r"[)\]]*\s+([a-z])", text[i + 1:])
        if char in "’ʼ'" and text[i - 1:i].lower() == "s" and following:
            after = i + 1 + following.start(1)
            if ((italic and not italic[after] or re.match(r"(?:and|or)\b", text[after:]))
                    and not re.match(r"(?:see|cf|note)\b", text[after:], re.I)
                    and any(c in text[i + 1:] for c in "’ʼ'")):
                continue
        if i == begin + 1 and char in CLOSE and text[begin] in "‘ʻ" and char in "’ʼ":
            continue  # Literal doubled opening marks in Word.
        if char in CLOSE + "“" and (i + 1 == len(text) or not text[i + 1].isalpha() or text[i + 1] in CLOSE):
            same_family = (char in "ʼ’ʾ'" and stack[-1] in "ʼ’ʾ'") or (char in '”"' and stack[-1] in '”"')
            if char == stack[-1] or same_family:
                stack.pop()
                if not stack:
                    return i
                continue
        if char in PAIRS and text[i - 1] in " \t\n(:" + OPEN and i + 1 < len(text) and not text[i + 1].isspace():
            # A transliterated name ('Aneze, ‘Iwardo) is not an opened
            # quotation. A nested single quote needs its own later closer.
            if char in "‘ʻ'" and stack[-1] in "’ʼ'":
                closers = re.findall(r"[’ʼ'](?=[^\w]|$)", text[i + 1:])
                literal = re.match(r"[^)\n]*?[’ʼ'](?=[^\w]|$)", text[i + 1:])
                if (len(closers) < 2 and not ENGLISH.match(text, i + 1)
                        and not (literal and re.search(r"\blit\.\s*$", text[:i]))):
                    continue
            stack.append(PAIRS[char])
    return None


def citation_match(text, begin):
    """Return a literal citation token, including a complete source wrapper.

    A parenthesis containing prose is not a citation list. Existing contextual
    recording locators and personal communications retain their literal wrapper.
    """
    attribution = re.match(r"[-–—]\s+Shabo(?=\s*;)", text[begin:])
    if attribution:
        return attribution[0], "source", begin + attribution.end()
    if begin < len(text) and text[begin] == "(":
        labelled = re.match(rf"\(No \d+:\s*{RECORDING}\)?", text[begin:])
        if labelled:
            return labelled[0], "source", begin + labelled.end()
        close = text.find(")", begin + 1)
        if close >= 0 and "(" not in text[begin + 1:close]:
            inside = text[begin + 1:close]
            refs, end = refs_at_start(inside)
            if ((refs and not inside[end:].strip())
                    or re.fullmatch(rf"(?:Nisane\s+{DATE}|{DATE}\s+Nisane|Nisane first interview|Sultan_Nisane)", inside, re.I)):
                return text[begin:close + 1], "context", close + 1
    if begin < len(text) and text[begin] in "‘ʻ'":
        match = re.match(RECORDING, text[begin + 1:])
        if match:
            end = begin + 1 + match.end()
            if end < len(text) and text[end] in "’ʼ'":
                return text[begin:end + 1], "source", end + 1
    match = REF.match(text, begin)
    if match:
        return match[0], match.lastgroup, match.end()
    return None


def citation_start(text, start, end=None):
    """Find a citation at a lexical boundary, never a number in narrative prose."""
    limit = len(text) if end is None else min(end, len(text))
    depth = 0
    for i in range(start, limit):
        if text[i] == ")":
            depth = max(0, depth - 1)
        if depth:
            if text[i] == "(":
                depth += 1
            continue
        if text[i] == "(" and not citation_match(text, i):
            depth += 1
            continue
        if i > start and (text[i - 1].isalnum() or text[i - 1] in "_-" ):
            continue
        if text[i:i + 1].isalpha() and i and text[i - 1] == "." and re.search(r"\d[\w.]*_$", text[:i]):
            continue
        token = citation_match(text, i)
        if not token:
            continue
        raw, kind, stop = token
        if raw == "Shabo" and text[stop:].lstrip()[:1] not in ";.)\n":
            continue
        if kind == "page" and (i == 0 or text[:i].rstrip()[-1:] not in ";" + CLOSE):
            continue
        if stop < len(text) and text[stop] not in " \t\n;,.)[" and not (kind == "text" and text[stop].isupper()) and not (raw.startswith("(") and text[stop] == "/"):
            continue
        return i
    return None


def refs_at_start(text, start=0):
    """Consume only citation tokens, never scan arbitrary example prose for digits."""
    result, pos = [], start
    while True:
        delimiter = re.match(r"[\s;,]*", text[pos:])
        begin = pos + delimiter.end()
        if "\n" in delimiter[0]:
            # A new example can start with its source label or verse number.
            # Consume a citation paragraph only when the whole line is a cite.
            line = text[begin:].split("\n", 1)[0]
            found, tail = refs_at_start(line)
            if not found or line[tail:].strip():
                return result, begin
        if NUMBER.match(text, begin):
            return result, begin
        match = citation_match(text, begin)
        if not match:
            return result, begin
        raw, group, end = match
        # A bare page must end at punctuation/whitespace, not inside a word/date.
        if end < len(text) and text[end] not in " \t\n;,.)[" and not (group == "text" and text[end].isupper()) and not (raw.startswith("(") and text[end] == "/"):
            return result, begin
        if group == "page" and re.fullmatch(r"\d", raw) and re.match(r"\s+k-", text[end:]):
            return result, begin
        if group == "page" and re.match(r"\.(?:\d|\s+\S)", text[end:]):
            return result, begin
        kind, text_id, verse = "other", None, None
        if group == "prefixed":
            prefix = re.match(r"[A-Za-z]+", raw)[0].lower()
            kind = {"prs": "prs", "jl": "jl", "lb": "lb", "mm": "mm", "luf": "luf"}.get(prefix, "other")
        elif group == "text":
            number, v = re.match(r"(\d+)/(\d+)", raw).groups()
            kind, text_id, verse = "text", f"R{int(number):03d}", int(v)
        elif group == "page":
            kind = "grammar-page"
        result.append({"raw": raw, "kind": kind, "textId": text_id, "verse": verse})
        pos = end


# Only explicit English syntax is a fallback when source formatting is absent
# or inverted. In particular, Turoyo's article "I" alone is not an English cue.
ENGLISH = re.compile(
    r"(?:(?:I|we|you|he|she|they|it)\s+(?:am|are|is|was|were|will|would|shall|should|can|could|must|have|has|had|do|does|did|went|dug|got|spent|rely|support|claspes|clasped|killed|liked|reached|gave|picked|plunged|changed|threw|swears|says|said|put|promised|trampled)\b"
    r"|(?:are|is|did|does|do|can|could|will|would)\s+(?:they|he|she|it|there|you|we|the)\b"
    r"|(?:the|this|that|those|all|nine|people|smoking|leaves|grapes)\s+"
    r"|(?:now|then|once|well|songs|oh|so|today|till)\b[,!?.]?\s+|(?:yes|no)[,!]\s+"
    r"|(?:and|but|because|in)\s+(?:the|this|that|he|she|they|we|all|Bakkoye)\b|as\s+long\b"
    r"|is exactly the same as\b|does\s+not\b|tea\s+dissolved\b|are\s+the\b|my\s+life\b|because\s+of\b"
    r"|(?:my|your|his|her|our|their)\s+\w+\s+(?:was|is|were|are|has|have)\b"
    r"|damned\s+by\b|Naturally,?\s+|Finally,?\s+|A\s+snake\s+passed\b"
    r"|(?:They|He|She)\s+\([^()]+\)\s+(?:brought|comes|will|said)\b"
    r"|\[The\s+king\]\s+said\b|Nisane,\s+her\s+grandmother\b"
    r"|(?-i:[A-Z][a-z]+)(?:\s+and\s+(?-i:[A-Z][a-z]+))?\s+(?:did|does|was|were|has|have|is|are|will|induced|moved|made|remained|bring|becomes|drafts|craved|stole)\b)",
    re.I,
)


TUROYO = re.compile(r"[əәǝ]|\w[=+]\w|\w+-(?:yo|no)\b")
SPEECH = re.compile(r"(?:kom[aeə]r|om[aeə]r|m[əǝ]rla|m[əǝ]ḷḷe|məlle|kәmmo|[əƏәǝ]mm[io]|koḥayri)\s*[,.:]?\s*$", re.I)


def direct_speech(prefix, content):
    if (ENGLISH.match(content.lstrip())
            or re.match(r"\S+\s+(?:said to\b|bedeutet:)", content)):
        return False
    return bool(re.match(r"(?:Ono|Hani|Mən|Hawli|Haw|Elux|Raq|Hə|Tiqo)\b", content, re.I)
                or re.match(r"Ha\b", content) and TUROYO.search(content)
                or TUROYO.search(content.split(" ", 1)[0]) or
                SPEECH.search(prefix) and (re.search(r"[əәǝʕʔḏḥṭṣšġǧṯḷ]", content[:50]) or
                    re.match(r"(?:Yabo|Ha|Lo|Qay|Raq|Hə|Tiqo|zox|Ya ḥurma)\b", content, re.I)))


def gloss_end(text, start, end):
    citation = citation_start(text, start, end + 1)
    if citation is not None:
        end = citation
    while end > start and text[end - 1] in " \t\n;":
        end -= 1
    return end


def annotations(text, notes_only=False):
    """Balanced source comments/attributions, not parenthetical translations."""
    stack = []
    for i, char in enumerate(text):
        if char == "(":
            stack.append(i)
        elif char == ")" and stack:
            begin = stack.pop()
            if stack:
                continue
            inside = text[begin + 1:i]
            if (re.search(r"\bprefers\b|is obligatory|\bp\.?c\.?\b", inside, re.I)
                    or (not notes_only and TUROYO.search(inside))
                    or re.fullmatch(r"CS|sic!|Ilyas|Nisane, Ilyas’ sister|Ilyas from Kfarze [\d-]+", inside)):
                yield begin, i + 1
    # Standalone editorial/source labels in roman runs.
    for match in re.finditer(r"(?:According to Ido Talay|auch:|aus brix abgeleitet auch|fossilized in)\s*", text):
        yield match.start(), match.end()


def translation_span(value: Text, start=0):
    """Find the earliest gloss, using its letters rather than its quote's font.

    A citation after a closed quote is also decisive when the entire translation
    was accidentally italicised. Unquoted English is accepted only with explicit
    syntax; other unformatted material remains verbatim for proofreading.
    """
    text = value.text
    comments = list(annotations(text))
    initial = start + len(text[start:]) - len(text[start:].lstrip())
    candidates = [i for i in range(start, len(text))
                  if text[i] in OPEN and i > start and text[start:i].strip()
                  and (text[i - 1].isspace() or text[i - 1] in ":;,.!?" + OPEN
                       or value.italic and value.italic[i - 1] != value.italic[i])]
    if ((ENGLISH.match(text, initial) and not any(any(value.italic[initial:i]) for i in candidates))
            or re.match(r"(?:Dear\b|\S+ knows of no\b)", text[initial:])):
        return None
    quoted, fallback = None, None
    for begin in candidates:
        if any(a <= begin < b for a, b in comments) or citation_match(text, begin):
            continue
        prefix = NUMBER.sub("", text[start:begin], count=1).strip()
        if not any(c.isalpha() for c in prefix):
            continue
        if (not any(value.italic[start:begin])
                and re.fullmatch(r"[\w\s]{1,30}:\s*", text[start:begin])):
            continue
        citation = citation_start(text, begin + 1)
        line_end = next((m.end() for m in re.finditer(r"\n+", text[begin:])
                         if TUROYO.search(text[begin + m.end():].split(" ", 1)[0])), None)
        if line_end is not None:
            line_end += begin - 1
        limit = min(p for p in (len(text), citation, line_end) if p is not None and p >= 0)
        quote_text = text[:limit]
        end = closing_quote(quote_text, begin, value.italic)
        tr_start = begin + 1
        if text[tr_start:tr_start + 1] in "’ʼ" and text[begin] in "‘ʻ":
            tr_start += 1
        content_end = end if end is not None else len(quote_text)
        content = text[tr_start:content_end]
        cited = bool(refs_at_start(text, end + 1 if end is not None else content_end)[0])
        if (direct_speech(prefix, content)
                or not any(value.italic[start:begin]) and not cited
                and re.search(r"[əәǝʕʔḏḥṭṣšġǧṯḷ]", content)
                and not ENGLISH.match(content)):
            continue
        if end is None:
            end = tr_start
            while end < len(quote_text) and text[end] != "\n" and (not value.italic or not value.italic[end] or not text[end].isalpha()):
                end += 1
            # Wholly italic glosses require explicit English at the opening.
            if end == tr_start and ENGLISH.match(text, tr_start):
                end = text.find("\n", tr_start)
                if end < 0:
                    end = len(quote_text)
            end = gloss_end(text, tr_start, end)
            if end > tr_start:
                # Keep mismatched closing punctuation in raw, outside the gloss.
                tr_end = end
                while tr_end > tr_start and text[tr_end - 1] in CLOSE:
                    inner = text[tr_start:tr_end - 1]
                    if ((text[tr_end - 1] == "”" and "“" in inner)
                            or text[tr_end - 1] in "’ʼ" and any(c in inner for c in "‘ʻ")):
                        break
                    tr_end -= 1
                quoted = (begin, tr_start, tr_end, end)
                break
            continue
        consumed = end + 1
        while consumed < len(text) and text[consumed] in CLOSE:
            consumed += 1
        span = (begin, tr_start, end, consumed)
        letters = [j for j in range(tr_start, end) if text[j].isalpha()]
        roman = not value.italic or (letters and sum(not value.italic[j] for j in letters) > len(letters) / 2)
        cited = bool(refs_at_start(text, consumed)[0])
        if roman or cited or ENGLISH.match(text, tr_start):
            # Consecutive quoted replies/alternatives belong to this gloss.
            # Keep intervening source punctuation verbatim inside the span.
            while True:
                continuation = re.match(r"[ \t,–—-]*(?:(?:He|She) said:\s*)?([‘ʻ“\"'])", text[consumed:])
                if not continuation:
                    break
                next_begin = consumed + continuation.end() - 1
                citation = citation_start(text, next_begin + 1)
                next_end = closing_quote(text if citation is None else text[:citation], next_begin, value.italic)
                stop = next_end + 1 if next_end is not None else gloss_end(text, next_begin + 1, len(text))
                if stop <= next_begin + 1 or direct_speech("", text[next_begin + 1:stop]):
                    break
                span = (begin, tr_start, stop, stop)
                consumed = stop
            quoted = span
            break
        if fallback is None:
            fallback = span

    limit = quoted[0] if quoted else len(text)
    has_turoyo, roman_until, previous = False, start, start
    for match in re.finditer(r"\[The king\]|[^\W\d_]+", text[start:limit]):
        i = start + match.start()
        if "\n" in text[previous:i]:
            has_turoyo = False
        previous = i
        if value.italic and value.italic[i]:
            has_turoyo = True
        if not text[start:i].strip() or any(a <= i < b for a, b in comments):
            continue
        if i and not (text[i - 1].isspace() or text[i - 1] in "=([)–.?!:;"):
            continue
        english = ENGLISH.match(text, i)
        # An italic -> roman boundary is stronger than language heuristics.
        formatted = has_turoyo and value.italic and not value.italic[i] and i >= roman_until
        if not english and not formatted:
            continue
        roman_intro = (quoted and formatted and (len(text[i:quoted[0]].split()) >= 4
                       or re.match(r"(?:lit\.|is\b)", text[i:]))
                       and not TUROYO.search(text[i:quoted[0]].split("(", 1)[0]))
        if quoted and (not (english or roman_intro) or (value.italic and value.italic[i]
                       and not re.match(r"(?:He|She|They)\b", text[i:]))):
            continue
        if quoted and text[start:i].count("(") > text[start:i].count(")"):
            continue
        end = i
        while end < len(text):
            if (text[end] == "\n" and not (english and end < english.end())) or (not value.italic[i] and value.italic[end] and text[end].isalpha()):
                break
            end += 1
        suffix = re.match(r"[A-Za-z]+[.!?]", text[end:])
        if english and suffix and re.match(RECORDING, text[end + suffix.end():]):
            end += suffix.end()
        tail = text[i:end]
        if re.match(r"(?:Пример\b|Надо\b|Выпала\b|cf\.|see\b|Note\b|SL\b|turkish:|is preferred\b)", tail, re.I):
            continue
        refs, consumed = refs_at_start(text, i)
        if refs:
            roman_until = consumed
            continue
        roman_until = end
        if re.fullmatch(r"[\wʕʔḤİ. ,;-]*\bp\.?c\.?[\s).,;]*", tail, re.I):
            continue
        if (TUROYO.search(tail.split("(", 1)[0]) or re.match(r"[ʕʔ]", tail)) and not english and not quoted:
            continue
        if sum(c.isalpha() for c in tail) < 3:
            continue
        if re.search(r"\betc[.…]", tail) and text[:i].rstrip().endswith("("):
            continue
        # References and source labels can be roman too. End the gloss before
        # its citation, keeping the citation available to the same scanner.
        end = gloss_end(text, i, end)
        remarks = re.finditer(r"(?:\s+[–—]\s+Ilyas, spontaneous speech|(?:\s+|(?<=[.!?]))=\s+|We shall have to doublecheck\b|:\s*[^:\n]{1,30}:\s*[“‘ʻ])", text[i:end])
        remark = next((m for m in remarks if text[i:i + m.start()].count("(")
                       == text[i:i + m.start()].count(")")), None)
        if remark:
            end = i + remark.start()
        # Parentheses are also used as translation delimiters. Do not leave
        # their opening mark in Turoyo or absorb following Turoyo into English.
        before = text[:i].rstrip()
        if before.endswith("("):
            close, depth = i, 1
            while close < len(text) and depth:
                depth += (text[close] == "(") - (text[close] == ")")
                close += 1
            if not depth:
                consumed = close if end >= close - 1 else end
                # A parenthetical gloss can finish inside a native quotation.
                # Its outer closing mark precedes the recording attribution.
                if (consumed == close and close < len(text) and text[close] in CLOSE
                        and re.match(rf"\s*{RECORDING}", text[close + 1:])):
                    consumed += 1
                return len(before) - 1, i, min(end, close - 1), consumed
        return i, i, end, end
    return quoted or fallback


def source_start(value, start):
    """A supported source passage after citations and editorial remarks.

    Skip balanced annotations and Cyrillic editorial text only at this already
    established boundary. Never search arbitrarily inside a bilingual passage.
    """
    text = value.text
    pos = start
    after_note = False
    while pos < len(text):
        skip = re.match(r"[\s;,.–—-]+|\([^()\n]*\)|\[[^]\n]*\]", text[pos:])
        if skip:
            after_note = after_note or skip[0].startswith(("(", "["))
            pos += skip.end()
            continue
        refs, end = refs_at_start(text, pos)
        if refs and end > pos and after_note:
            pos = end
            continue
        label = re.match(r"(?:According to Ido Talay|auch:|aus brix abgeleitet auch|fossilized in)\s+", text[pos:])
        if label:
            pos += label.end()
            continue
        editorial = re.match(r"See also [^;\n]+;\s*", text[pos:], re.I)
        if editorial:
            pos += editorial.end()
            after_note = True
            continue
        if re.match(r"[А-Яа-яЁё]", text[pos:]):
            # Stop at the next Latin source word after a Cyrillic remark.
            # Quoted Russian prose remains with the remark.
            remark = re.match(r"[А-Яа-яЁё\s,;.!?:–—\-()«»“”‘’]+", text[pos:])
            pos += remark.end()
            after_note = True
            continue
        break
    if pos >= len(text) or re.match(r"(?:cf\.|see\b|Note\b|SL\b|where\b|preterit\b|Idiom\b|MUST\b|According to\b|auch:|aus\b|fossilized\b)", text[pos:], re.I):
        return None
    first = text[pos:].split("\n", 1)[0]
    if ENGLISH.match(first) or re.search(r"\b(?:also knows this verb|knows of no)\b", first):
        return None
    if "\t" in first:
        return None
    marker = NUMBER.search(first)
    if marker:
        first = first[:marker.start()]
    if after_note:
        passage = value.cut(pos, pos + len(first))
        gloss = translation_span(passage)
        cite = citation_start(first, 1)
        if ((gloss is None and (cite is None or len(first[:cite].split()) < 3))
                or gloss is not None and not refs_at_start(first, gloss[3])[0]):
            return None
    variant = re.match(r"(?:\d+[ab]\)\s*|\d(?=\s+k-)\s+)", first)
    body = first[variant.end():] if variant else first.lstrip("«“‘ʻ\"'")
    if re.match(r"\S+[’ʼ],\s*i[+=]maʕnay", body):
        return None
    if re.match(r"\d+[.]\s+", body):
        body = re.sub(r"^\d+[.]\s+", "", body)
    is_source = (value.italic and value.italic[pos]) or re.search(r"[əәǝʕʔḏḥṭṣšġǧṯḷ]", body)
    if is_source and (text[pos].isalpha() or text[pos] in "«“‘ʻ\"'" or variant or re.match(r"\d+[.]\s+", text[pos:])):
        return pos
    return None


def source_quotes(value):
    """Closed native speech, whose internal timestamps are not tail citations."""
    text = value.text
    stop = 0
    for i, char in enumerate(text):
        if i < stop or char not in OPEN:
            continue
        end = closing_quote(text, i, value.italic)
        if end is not None and direct_speech(text[:i], text[i + 1:end]):
            yield i, end + 1
            stop = end + 1


def split_examples(value: Text, initial_sense=None):
    """Return raw-preserving (sense, rich text) pairs; inherit a numbered group."""
    text = value.text
    # Paragraphs are reliable boundaries, except a separately typed translation
    # or citation paragraph, which belongs to the preceding example.
    boundaries = {0, len(text)}
    for match in re.finditer(r"\n+", text):
        after = text[match.end():]
        if after.strip() and not after.lstrip().startswith(tuple(OPEN)):
            refs, end = refs_at_start(after)
            if (not refs or after[end:].strip()) and not ENGLISH.match(after.lstrip()):
                boundaries.add(match.end())
    # Parenthesised citations contain timestamps such as '(209 FG 15: 04)'.
    # Their closing minutes are not numbered senses, nor are numbers in glosses.
    protected, glosses = [], []
    # A translation + citations ends an example even within one paragraph.
    pos = 0
    while pos < len(text):
        span = translation_span(value, pos)
        if span is None:
            break
        _, _, _, end = span
        protected.append((span[0], end))
        glosses.append((span[0], end))
        boundaries = {b for b in boundaries if b == 0 or b == len(text)
                      or not (span[0] <= b < end or b <= span[0] and not text[b:span[0]].strip())}
        _, tail = refs_at_start(text, end)
        boundaries = {b for b in boundaries if b == 0 or b == len(text) or not end <= b < tail}
        # A passage may have several Turoyo paragraphs followed by one English
        # paragraph. Join the unfinished paragraphs, but retain boundaries after
        # a preceding translated or explicitly cited example.
        if span[0] == span[1]:
            line = text.rfind("\n", pos, span[0]) + 1
            if not text[line:span[0]].strip() or re.fullmatch(r"\d+[:.]\s*", text[line:span[0]]):
                boundaries.discard(line)
                preceding = sorted(b for b in boundaries if pos < b < line)
                for boundary in reversed(preceding):
                    previous = text[text.rfind("\n", pos, boundary - 1) + 1:boundary]
                    if refs_at_start(previous)[0] or re.search(r";\s*$", previous) or NUMBER.match(text, boundary):
                        break
                    boundaries.discard(boundary)
        next_start = source_start(value, tail)
        if next_start is not None:
            boundaries.add(next_start)
            tail = next_start
        if next_start is None and re.match(r"[‘ʻ]\S+[’ʼ],\s*i[+=]maʕnay", text[tail:]):
            # Keep the intervening uncertain comparison in its existing note.
            # Its last roman -> italic transition resumes the native passage.
            for j in reversed(range(tail + 1, len(text))):
                if (value.italic and value.italic[j] and not value.italic[j - 1]
                        and text[j].isalpha() and text[tail:j].rstrip().endswith(";")
                        and len(text[j:].split()) >= 5 and TUROYO.search(text[j:j + 60])
                        and "\n" not in text[tail:j]):
                    next_start = source_start(value, j)
                    if next_start is not None:
                        boundaries.add(next_start)
                        tail = next_start
                        break
        if next_start is None and tail in boundaries and tail > pos:
            pos = tail
            continue
        if next_start is None:
            # The remainder is a note until an existing paragraph/sense
            # boundary. Do not discover new glosses inside that note.
            following = [b for b in boundaries if b > tail]
            following.extend(m.start() for m in NUMBER.finditer(text, tail)
                             if text[m.start() - 1:m.start()] != "№")
            stop = min(following, default=len(text))
            protected.append((tail, stop))
            pos = max(stop, pos + 1)
        else:
            pos = max(end, tail, pos + 1)
    # These explicit editorial connectors introduce a following source form,
    # rather than an English gloss of the preceding form.
    for connector in re.finditer(r"(?:According to Ido Talay|auch:|aus brix abgeleitet auch|fossilized in)\s+", text):
        if any(a <= connector.start() < b for a, b in glosses):
            continue
        next_start = source_start(value, connector.end())
        if next_start is not None:
            line = text.rfind("\n", 0, connector.start()) + 1
            if not text[line:connector.start()].strip():
                boundaries.discard(next_start)
                boundaries.add(line)
            elif (connector[0].startswith("According to")
                  and any(b <= connector.start() for _, b in glosses)):
                # Preserve a label introducing the following form with that
                # form; do not reassign its attribution to the preceding gloss.
                boundaries.discard(next_start)
                boundaries.add(connector.start())
            else:
                boundaries.add(next_start)
    cursor = 0
    while cursor < len(text):
        cite = citation_start(text, cursor)
        if cite is None:
            break
        refs, tail = refs_at_start(text, cite)
        if not refs or tail <= cite:
            cursor = cite + 1
            continue
        previous = max((b for b in boundaries if b <= cite), default=0)
        if (text[previous:cite].strip() and any(c.isalpha() for c in text[previous:cite])
                and not any(a <= cite < b for a, b in protected)
                and not any(a <= cite < b for a, b in source_quotes(value))):
            next_start = source_start(value, tail)
            if next_start is not None and not re.search(r"According to Ido Talay\s*$", text[:next_start]):
                boundaries.add(next_start)
        cursor = max(tail, cite + 1)
    depth = 0
    markers = {m.start(): m for m in NUMBER.finditer(text)}
    for i, char in enumerate(text):
        if char in "([":
            depth += 1
        elif char in ")]":
            depth = max(0, depth - 1)
        if i in markers and text[i - 1:i] != "№" and not depth and not any(a <= i < b for a, b in protected):
            boundaries.add(i)
    cuts = sorted(boundaries)
    current_sense, result, pending = initial_sense, [], None
    for begin, end in zip(cuts, cuts[1:]):
        part = value.cut(begin, end)
        if not part.text.strip():
            continue
        if pending:
            part, pending = join([pending, part], ""), None
        refs, tail = refs_at_start(part.text)
        if result and refs and not part.text[tail:].strip():
            n, previous = result[-1]
            result[-1] = n, join([previous, part], "")
            continue
        if re.fullmatch(r"\s*[a-z]\)\s*", part.text):
            pending = part
            continue
        marker = NUMBER.match(part.text.lstrip())
        if marker:
            current_sense = marker[1]
        result.append((current_sense, part))
    if pending:
        result.append((current_sense, pending))
    return result


def parse_example(value: Text, sense, identifier):
    raw = value.text.strip()
    left = len(value.text) - len(value.text.lstrip())
    value = value.cut(left, left + len(raw))
    marker = NUMBER.match(raw)
    start = marker.end() if marker else 0
    span = translation_span(value, start)
    translation, note, refs = None, None, []
    if span:
        begin, tr_start, tr_end, end = span
        turoyo = raw[start:begin].strip()
        translation = raw[tr_start:tr_end].strip() or None
        refs, tail = refs_at_start(raw, end)
        note = raw[tail:].strip() or None
    else:
        # Without a translation, only a citation-looking tail after punctuation
        # can be extracted safely. Keep everything else in the original raw.
        turoyo = raw[start:].strip()
        offset = citation_start(raw, start + 1)
        internal_attribution = False
        if offset is not None and any(c.isalpha() for c in raw[start:offset]):
            found, tail = refs_at_start(raw, offset)
            # A slash introducing another untranslated variant makes this an
            # internal attribution. Keep the ambiguous passage intact.
            internal_attribution = raw[tail:].lstrip().startswith("/")
            if not internal_attribution:
                turoyo = raw[start:offset].rstrip("; \t\n")
                refs, note = found, raw[tail:].strip() or None
        if not refs and not internal_attribution:
            comment = next(((a, b) for a, b in annotations(raw, notes_only=True) if a >= start), None)
            if comment:
                turoyo = raw[start:comment[0]].strip()
                note = raw[comment[0]:].strip()
        if not refs and not note and not any(flag and char.isalpha() for char, flag in zip(value.text, value.italic)):
            note = raw
    return {"id": identifier, "sense": sense, "turoyo": turoyo,
            "translation": translation, "refs": refs, "note": note, "raw": raw}

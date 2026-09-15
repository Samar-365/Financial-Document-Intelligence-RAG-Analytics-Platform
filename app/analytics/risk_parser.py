"""Risk Factor Disclosure Parser for financial documents (Module 9.1).

Responsible for:
1. Identifying Item 1A / Risk Disclosures section boundaries across document chunks.
2. Filtering out Table of Contents (TOC) noise and dotted page markers.
3. Eliminating generic regulatory safe-harbor boilerplate and forward-looking statement disclaimers.
4. Preserving substantive operational, strategic, and financial threat disclosures for downstream classification.
"""

import re
from typing import List, Optional
from app.document_processing.metadata_tagger import TextChunkDTO #TextChunkDTO carries text and page provenance


class RiskDisclosureParser:
    """Scans document text chunks to isolate qualitative risk factor disclosures (Item 1A / Principal Risks).

    Technical Tasks:
    1. Item 1A Section Locator: Scan document chunks for Item 1A / Risk Disclosures headers and isolate candidate risk paragraphs.
    2. Boilerplate Noise Filtering: Filter out standard generic regulatory disclaimers using keyword heuristics to retain specific business threats.
    """

    #Regex pattern detecting the start of Item 1A or equivalent annual report risk section headers
    RISK_SECTION_START_PATTERN: re.Pattern = re.compile(
        r"(?i)(?:^|[\n\r])\s*(?:#+\s*)?(?:"
        r"item\s+1a[\.\:\s\-–—]+(?:risk\s+factors)?|"
        r"risk\s+factors|"
        r"principal\s+risks(?:\s+and\s+uncertainties)?|"
        r"key\s+(?:business\s+)?risks|"
        r"risk\s+disclosures|"
        r"risks\s+related\s+to\s+our\s+business|"
        r"risk\s+management\s+and\s+internal\s+controls|"
        r"statement\s+of\s+principal\s+risks"
        r")\b",
        re.MULTILINE,
    ) #Matches standard Item 1A and annual report risk section header variations

    #Regex pattern detecting subsequent major filing items that mark the exit from Item 1A
    SECTION_EXIT_PATTERN: re.Pattern = re.compile(
        r"(?i)(?:^|[\n\r])\s*(?:#+\s*)?(?:"
        r"item\s+1b[\.\:\s\-–—]+(?:unresolved\s+staff\s+comments)?|"
        r"item\s+1c[\.\:\s\-–—]+(?:cybersecurity)?|"
        r"item\s+2[\.\:\s\-–—]+(?:properties)?|"
        r"item\s+3[\.\:\s\-–—]+(?:legal\s+proceedings)?|"
        r"item\s+4[\.\:\s\-–—]+(?:mine\s+safety\s+disclosures)?|"
        r"item\s+7[\.\:\s\-–—]+(?:management'?s\s+discussion\s+and\s+analysis)?|"
        r"item\s+8[\.\:\s\-–—]+(?:financial\s+statements\s+and\s+supplementary\s+data)?"
        r")\b",
        re.MULTILINE,
    ) #Marks the formal transition into subsequent SEC 10-K sections

    #Regex detecting Table of Contents (TOC) dot leader patterns and index listings
    TOC_PATTERN: re.Pattern = re.compile(
        r"(?:\.{3,}\s*\d+)|(?:table\s+of\s+contents)",
        re.IGNORECASE,
    ) #Identifies leader dots or explicit TOC banners so index pages are not misclassified

    #Keywords identifying generic legal safe-harbor and statutory disclaimer text
    BOILERPLATE_PHRASES: List[str] = [
        "cautionary note regarding forward-looking statements",
        "forward-looking statements within the meaning of section 27a",
        "private securities litigation reform act of 1995",
        "safe harbor statement under the private securities",
        "safe harbor statement under the us private securities",
        "words such as \"anticipate,\"",
        "words such as 'anticipate,'",
        "actual results could differ materially",
        "actual results may differ materially",
        "undertake no obligation to publicly update",
        "we undertake no obligation to update",
        "indicate by check mark whether the registrant",
        "pursuant to the requirements of section 13",
        "pursuant to the requirements of the securities exchange act",
    ] #Common generic regulatory formulas that contain zero substantive risk disclosures

    #Keywords indicating concrete, substantive business threats and vulnerabilities
    SUBSTANTIVE_RISK_KEYWORDS: List[str] = [
        "adverse", "adversely", "loss", "losses", "decline", "declining",
        "threat", "impair", "impairment", "fail", "failure", "disrupt",
        "disruption", "volatility", "breach", "cyber", "litigation", "lawsuit",
        "liability", "default", "inflation", "supply chain", "competitor",
        "competition", "shortage", "sanction", "investigation", "recession",
        "vulnerability", "exposure", "concentration", "counterparty",
    ] #Concrete threat terms characteristic of actionable risk disclosures

    def locate_risk_sections(self, chunks: List[TextChunkDTO]) -> List[TextChunkDTO]:
        """Extracts and filters candidate risk factor disclosure chunks from document chunks.

        Sequential chunks are tracked to capture contiguous Item 1A disclosures between
        the Item 1A start header and subsequent exit section headers (e.g., Item 1B/2/7).
        Additionally, standalone chunks with prominent risk headings are detected even
        if chunks are supplied out-of-sequence.

        Args:
            chunks: List of TextChunkDTO metadata objects from document processing.

        Returns:
            List[TextChunkDTO]: Substantive, non-boilerplate risk factor chunks.

        Raises:
            TypeError: If chunks is not a list or elements are not TextChunkDTO instances.
        """
        if not isinstance(chunks, list): #Validate that the input is a list
            raise TypeError("chunks must be a list of TextChunkDTO instances.")

        if not chunks: #Fast exit on empty chunk input
            return []

        for idx, chunk in enumerate(chunks): #Validate each element is indeed a TextChunkDTO instance
            if not isinstance(chunk, TextChunkDTO):
                raise TypeError(
                    f"Element at index {idx} in chunks is {type(chunk).__name__}, expected TextChunkDTO."
                )

        isolated_risk_chunks: List[TextChunkDTO] = [] #Collector for verified risk disclosure chunks
        in_risk_section: bool = False #State flag tracking whether current reading cursor is inside Item 1A

        for chunk in chunks: #Iterate sequentially through document chunks
            content = chunk.content #Extract chunk text

            #Step 1: Check if chunk is a Table of Contents (TOC) page
            if self.is_table_of_contents(content): #Skip TOC lines so they do not trigger risk section state
                continue

            #Step 2: Check for exit section header indicating end of Item 1A
            if in_risk_section and self.is_section_exit_header(content):
                #Check if chunk starts with the exit header, or transitions mid-chunk
                in_risk_section = False #Flip state flag to false upon encountering next major item

            #Step 3: Check for risk section start header
            has_start_header = self.is_risk_section_header(content) #Test for Item 1A / Risk Factors header
            if has_start_header:
                in_risk_section = True #Activate risk section collection state

            #Step 4: Determine if chunk is candidate risk content (active state or standalone risk chunk)
            is_standalone = self._is_standalone_risk_chunk(content) #Check if chunk has standalone risk headings
            if in_risk_section or is_standalone:
                #Step 5: Filter out generic legal boilerplate
                if self.is_boilerplate(content): #Skip generic forward-looking safe harbor disclaimers
                    continue

                #Step 6: Filter out non-substantive or pure empty/table chunks
                if not self.is_substantive_risk_chunk(chunk): #Validate minimum length and substantive keywords
                    continue

                isolated_risk_chunks.append(chunk) #Retain verified substantive risk chunk

        return isolated_risk_chunks #Return all isolated and filtered risk chunks

    def is_risk_section_header(self, text: str) -> bool:
        """Determines if the text contains an Item 1A or Risk Factors start header.

        Args:
            text: Text content of the chunk.

        Returns:
            bool: True if a start header is identified, False otherwise.
        """
        if not text or not text.strip(): #Validate non-empty text
            return False
        return bool(self.RISK_SECTION_START_PATTERN.search(text)) #Search for risk header regex match

    def is_section_exit_header(self, text: str) -> bool:
        """Determines if the text contains an exit header marking the end of Item 1A.

        Args:
            text: Text content of the chunk.

        Returns:
            bool: True if an exit header (e.g. Item 1B, Item 2) is identified, False otherwise.
        """
        if not text or not text.strip(): #Validate non-empty text
            return False
        return bool(self.SECTION_EXIT_PATTERN.search(text)) #Search for exit section regex match

    def is_table_of_contents(self, text: str) -> bool:
        """Identifies whether a chunk is part of a Table of Contents rather than disclosure text.

        Args:
            text: Text content of the chunk.

        Returns:
            bool: True if TOC characteristics are detected, False otherwise.
        """
        if not text or not text.strip(): #Validate non-empty text
            return False

        #Check for leader dots followed by page numbers, e.g., 'Item 1A. Risk Factors ......... 14'
        if self.TOC_PATTERN.search(text): #Check for TOC dot patterns
            return True

        #Detect multiple Item listings packed together in a concise block (typical TOC structure)
        item_mentions = len(re.findall(r"(?i)\bitem\s+(?:1|1a|1b|1c|2|3|4|5|6|7|8)\b", text))
        if item_mentions >= 2 and len(text.split()) < 150: #Multiple items in short chunk indicates TOC
            return True

        return False #Not a TOC chunk

    def is_boilerplate(self, text: str) -> bool:
        """Identifies generic regulatory safe-harbor disclaimers and legal noise.

        Calculates boilerplate phrase hits and compares them against substantive risk terms
        to differentiate generic legal disclaimers from genuine business threat disclosures.

        Args:
            text: Text content of the chunk.

        Returns:
            bool: True if chunk is predominantly boilerplate noise, False if substantive.
        """
        if not text or not text.strip(): #Validate non-empty text
            return False

        lower_text = text.lower() #Convert to lowercase for case-insensitive matching

        #Check for direct hits on known generic safe-harbor phrases
        boilerplate_hits = sum(1 for phrase in self.BOILERPLATE_PHRASES if phrase in lower_text)

        #Check for substantive business threat keywords
        substantive_hits = sum(1 for kw in self.SUBSTANTIVE_RISK_KEYWORDS if kw in lower_text)

        #Case 1: Standard cautionary note / safe harbor header with low substantive threat content
        if "cautionary note regarding forward-looking statements" in lower_text:
            if substantive_hits <= 2: #Safe-harbor disclaimer with little to no concrete threat details
                return True

        #Case 2: Forward-looking statements under PSLRA 1995 or SEC Section 27A
        if "private securities litigation reform act" in lower_text or "section 27a of the securities act" in lower_text:
            if substantive_hits <= 2: #Statutory boilerplate with minimal operational risk substance
                return True

        #Case 3: Procedural SEC check-box or filing signatory boilerplate
        if "indicate by check mark" in lower_text or "pursuant to the requirements of section 13" in lower_text:
            return True #Pure SEC administrative boilerplate

        #Case 4: High ratio of generic boilerplate phrases relative to substantive keywords
        if boilerplate_hits >= 2 and substantive_hits <= 1:
            return True #Boilerplate outweighs concrete risk content

        return False #Contains substantive business risk content

    def is_substantive_risk_chunk(self, chunk: TextChunkDTO) -> bool:
        """Validates that a chunk contains substantive qualitative risk statements.

        Filters out very short fragments (< 60 chars), introductory title lead-ins,
        or pure financial data tables that lack qualitative risk narrative.

        Args:
            chunk: TextChunkDTO candidate chunk.

        Returns:
            bool: True if chunk contains substantive risk statements, False otherwise.
        """
        content = chunk.content.strip() #Strip whitespace

        if len(content) < 60: #Chunks under 60 characters are typically section headers or orphan titles
            return False

        #Pure table chunks without risk narrative are excluded
        if chunk.is_table_chunk:
            #If it is a table chunk, check if it contains qualitative risk narrative
            words = content.split()
            if len(words) < 20: #Very small table chunk with no narrative
                return False

        lower_content = content.lower() #Convert to lowercase

        #Strip section start headers and generic title repetitions so introductory lead-ins don't falsely qualify
        body_text = self.RISK_SECTION_START_PATTERN.sub("", lower_content)
        body_text = re.sub(
            r"(?i)\b(?:risk\s+disclosures?|risk\s+factors?|principal\s+risks?|key\s+risks?)\b",
            "",
            body_text,
        ).strip()

        #Verify presence of at least one substantive risk keyword or remaining risk indicator in narrative body
        has_substantive = any(kw in body_text for kw in self.SUBSTANTIVE_RISK_KEYWORDS)
        has_residual_risk_term = bool(re.search(r"\brisks?\b", body_text))

        if not (has_substantive or has_residual_risk_term): #If chunk has neither substantive terms nor risk discussion
            return False

        return True #Chunk meets substantive qualitative risk disclosure criteria

    def _is_standalone_risk_chunk(self, text: str) -> bool:
        """Determines if a chunk contains an explicit risk section title or heading.

        Used when chunks are provided non-contiguously or out-of-order.

        Args:
            text: Text content of the chunk.

        Returns:
            bool: True if chunk contains a standalone risk heading, False otherwise.
        """
        standalone_patterns = [
            r"(?i)^\s*#+\s*.*(?:risk|threat|uncertaint).*", #Markdown header discussing risks
            r"(?i)\b(?:operational|market|credit|liquidity|regulatory|strategic|cybersecurity)\s+risks?\b", #Specific risk category header
            r"(?i)\brisks\s+related\s+to\s+(?:our\s+business|our\s+industry|our\s+operations|regulation)\b", #Section heading
        ] #Patterns representing explicit standalone risk discussion sections
        return any(re.search(pat, text, re.MULTILINE) for pat in standalone_patterns)

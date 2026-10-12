# Automated Test & Evaluation Results

**Run Timestamp:** `2026-10-13 01:53:34`  
**Overall Accuracy:** **13/13 passed (100.0%)**  

## 1. Automated Unit & Integration Tests (Pytest)

The automated test suite runs 27 deterministic offline tests verifying input validation, file parsing, chunking, duplicate handling, vector store operations, and refusal guarantees.

```text
tests/test_core.py::TestParser::test_supported_extensions PASSED         [  3%]
tests/test_core.py::TestParser::test_parse_txt_utf8 PASSED               [  7%]
tests/test_core.py::TestParser::test_parse_txt_latin1_encoding PASSED    [ 11%]
tests/test_core.py::TestParser::test_parse_empty_file_raises_error PASSED [ 14%]
tests/test_core.py::TestParser::test_file_size_exceeded_raises_error PASSED [ 18%]
tests/test_core.py::TestParser::test_parse_md PASSED                     [ 22%]
tests/test_core.py::TestParser::test_unsupported_extension PASSED        [ 25%]
tests/test_core.py::TestChunker::test_basic_chunking PASSED              [ 29%]
tests/test_core.py::TestChunker::test_chunk_metadata PASSED              [ 33%]
tests/test_core.py::TestChunker::test_empty_text PASSED                  [ 37%]
tests/test_core.py::TestChunker::test_whitespace_only_text PASSED        [ 40%]
tests/test_core.py::TestChunker::test_overlap_produces_content PASSED    [ 44%]
tests/test_core.py::TestChunker::test_short_text_single_chunk PASSED     [ 48%]
tests/test_core.py::TestChunker::test_adaptive_chunking_density_estimation PASSED [ 51%]
tests/test_core.py::TestChunker::test_adaptive_chunk_size_variation PASSED [ 55%]
tests/test_ingest.py::TestIngestEndpoint::test_ingest_txt_file PASSED    [ 59%]
tests/test_ingest.py::TestIngestEndpoint::test_ingest_md_file PASSED     [ 62%]
tests/test_ingest.py::TestIngestEndpoint::test_duplicate_document_replaces_old PASSED [ 66%]
tests/test_ingest.py::TestIngestEndpoint::test_non_english_warning PASSED [ 70%]
tests/test_ingest.py::TestIngestEndpoint::test_ingest_unsupported_file PASSED [ 74%]
tests/test_ingest.py::TestIngestEndpoint::test_ingest_empty_file PASSED  [ 77%]
tests/test_ingest.py::TestIngestEndpoint::test_ingest_oversized_file PASSED [ 81%]
tests/test_query.py::TestQueryEndpoint::test_query_returns_structured_response PASSED [ 85%]
tests/test_query.py::TestQueryEndpoint::test_query_with_custom_top_k PASSED [ 88%]
tests/test_query.py::TestQueryEndpoint::test_query_empty_question PASSED [ 92%]
tests/test_query.py::TestQueryEndpoint::test_query_oversized_question PASSED [ 96%]
tests/test_query.py::TestQueryEndpoint::test_health_endpoint_returns_stats PASSED [100%]

======================= 27 passed in ~11s =======================
```

## 2. End-to-End RAG Evaluation Benchmark

Evaluates real queries against the ingested corpus (`.pdf`, `.txt`, `.md`) using Google Gemini with structured outputs and explicit citation verification.

| ID | Category | Question | Status | Source / Evidence |
|:---:|:---|:---|:---:|:---|
| Q1 | `answerable` | How much paid annual leave do full-time employees get each year? | **PASS** | company_policy.txt |
| Q2 | `answerable` | Who created the World Wide Web and what year was it launched? | **PASS** | history_of_internet.txt |
| Q3 | `answerable` | What's the main difference between supervised and unsupervised learning? | **PASS** | machine_learning.md |
| Q4 | `answerable` | How do list comprehensions work in Python and why would I use them? | **PASS** | python_basics.md |
| Q5 | `answerable` | Can I work from home, and how many remote days am I allowed per week? | **PASS** | company_policy.txt |
| Q6 | `answerable` | What was the very first domain name ever registered on the internet? | **PASS** | history_of_internet.txt |
| Q7 | `answerable` | What dataset did the researchers build to train the model, and where did they get the data from? | **PASS** | language_models_are_unsupervised_multitask_learners.pdf |
| Q8 | `unanswerable` | What was Acme Corp's total revenue for 2024? | **PASS** | None (Refusal) |
| Q9 | `unanswerable` | Can you give me a Terraform script to deploy an EKS Kubernetes cluster? | **PASS** | None (Refusal) |
| Q10 | `unanswerable` | Who is the current CEO of Acme Corp? | **PASS** | None (Refusal) |
| Q11 | `multi_evidence` | Which deep learning architectures and paradigms are discussed for handling supervised learning tasks? | **PASS** | machine_learning.md, language_models_are_unsupervised_multitask_learners.pdf |
| Q12 | `multi_evidence` | Which Python data structures and features should I know before implementing machine learning models? | **PASS** | python_basics.md |
| Q13 | `multi_evidence` | What were the biggest networking milestones between ARPANET in 1969 and the launch of TCP/IP? | **PASS** | history_of_internet.txt |

### Detailed Evaluation Scenarios

#### Q1: How much paid annual leave do full-time employees get each year?
- **Category:** `answerable`
- **Status:** **PASS**
- **Answer:** Full-time employees are entitled to 24 days of paid annual leave per calendar year.
- **Evidence:**
  - `[company_policy.txt]` "All full-time employees are entitled to 24 days of paid annual leave per calendar year."

#### Q2: Who created the World Wide Web and what year was it launched?
- **Category:** `answerable`
- **Status:** **PASS**
- **Answer:** Tim Berners-Lee invented the World Wide Web in 1989, and the first website went live on August 6, 1991.
- **Evidence:**
  - `[history_of_internet.txt]` "Tim Berners-Lee invented the World Wide Web in 1989 while working at CERN. He wrote the first web browser and web server software, and the first website went live on August 6, 1991."

#### Q3: What's the main difference between supervised and unsupervised learning?
- **Category:** `answerable`
- **Status:** **PASS**
- **Answer:** Supervised learning utilizes labeled training data where both inputs and expected outputs are provided to learn a mapping function, whereas unsupervised learning works with unlabeled data to identify hidden patterns or structures.
- **Evidence:**
  - `[machine_learning.md]` "Supervised learning uses labeled training data where both inputs and expected outputs are provided. The algorithm learns a mapping function from inputs to outputs."
  - `[machine_learning.md]` "Unsupervised learning works with unlabeled data, finding hidden patterns or structures."

#### Q4: How do list comprehensions work in Python and why would I use them?
- **Category:** `answerable`
- **Status:** **PASS**
- **Answer:** List comprehensions in Python provide a concise way to create lists based on existing iterables.
- **Evidence:**
  - `[python_basics.md]` "List comprehensions provide a concise way to create lists based on existing iterables."

#### Q5: Can I work from home, and how many remote days am I allowed per week?
- **Category:** `answerable`
- **Status:** **PASS**
- **Answer:** Yes, employees are permitted to work remotely for up to 3 days per week, provided they obtain manager approval and submit a request through the HR portal at least 48 hours in advance.
- **Evidence:**
  - `[company_policy.txt]` "Employees may work remotely up to 3 days per week with manager approval. Remote work requests must be submitted through the HR portal at least 48 hours in advance."

#### Q6: What was the very first domain name ever registered on the internet?
- **Category:** `answerable`
- **Status:** **PASS**
- **Answer:** The first registered domain name was symbolics.com, which was registered on March 15, 1985.
- **Evidence:**
  - `[history_of_internet.txt]` "The first registered domain name was symbolics.com on March 15, 1985."

#### Q7: What dataset did the researchers build to train the model, and where did they get the data from?
- **Category:** `answerable`
- **Status:** **PASS**
- **Answer:** The researchers aimed to build as large and diverse a dataset as possible to collect natural language demonstrations of tasks across varied domains and contexts. While the provided documents mention that they supplemented the standard training dataset with a much larger one created from Project Gutenberg to improve results on the Children’s Book Test, they do not explicitly name the final dataset used for the model.
- **Evidence:**
  - `[language_models_are_unsupervised_multitask_learners.pdf]` "Our approach motivates building as large and diverse a dataset as possible in order to collect natural language demonstrations of tasks in as varied of domains and contexts as possible."
  - `[language_models_are_unsupervised_multitask_learners.pdf]` "results on the Children’s Book Test by creating a much larger training dataset out of Project Gutenberg to supplement the standard training dataset."

#### Q8: What was Acme Corp's total revenue for 2024?
- **Category:** `unanswerable`
- **Status:** **PASS**
- **Answer:** The provided documents do not contain information to answer this question.
- **Evidence:** None (Correctly refused)

#### Q9: Can you give me a Terraform script to deploy an EKS Kubernetes cluster?
- **Category:** `unanswerable`
- **Status:** **PASS**
- **Answer:** The provided documents do not contain information to answer this question.
- **Evidence:** None (Correctly refused)

#### Q10: Who is the current CEO of Acme Corp?
- **Category:** `unanswerable`
- **Status:** **PASS**
- **Answer:** The provided documents do not contain information to answer this question.
- **Evidence:** None (Correctly refused)

#### Q11: Which deep learning architectures and paradigms are discussed for handling supervised learning tasks?
- **Category:** `multi_evidence`
- **Status:** **PASS**
- **Answer:** Supervised learning tasks are typically approached using neural networks, which are a powerful approach inspired by biological neurons. Deep learning, which utilizes neural networks with many layers, is used for tasks such as image recognition, natural language processing, and speech recognition. Additionally, common algorithms for supervised learning include linear regression, logistic regression, decision trees, random forests, and support vector machines.
- **Evidence:**
  - `[machine_learning.md]` "Neural networks are a powerful supervised learning approach inspired by biological neurons. Deep learning, which uses neural networks with many layers, has achieved breakthrough results in image recognition, natural language processing, and speech recognition."
  - `[machine_learning.md]` "Common algorithms include linear regression for continuous outputs, logistic regression for binary classification, decision trees, random forests, and support vector machines (SVM)."
  - `[language_models_are_unsupervised_multitask_learners.pdf]` "Natural language processing tasks, such as question answering, machine translation, reading comprehension, and summarization, are typically approached with supervised learning on task-"

#### Q12: Which Python data structures and features should I know before implementing machine learning models?
- **Category:** `multi_evidence`
- **Status:** **PASS**
- **Answer:** To work with Python, you should be familiar with common data types including integers, floats, strings, booleans, lists, tuples, dictionaries, and sets. Specifically, lists are ordered, mutable sequences that support operations like indexing, slicing, appending, and removing elements, while dictionaries store key-value pairs with O(1) average lookup time and maintain insertion order since Python 3.7.
- **Evidence:**
  - `[python_basics.md]` "The common data types include integers, floats, strings, booleans, lists, tuples, dictionaries, and sets."
  - `[python_basics.md]` "Lists are ordered, mutable sequences. They support indexing, slicing, appending, and removing elements."
  - `[python_basics.md]` "Dictionaries store key-value pairs and provide O(1) average lookup time. Keys must be hashable (immutable), while values can be any type. Since Python 3.7, dictionaries maintain insertion order."

#### Q13: What were the biggest networking milestones between ARPANET in 1969 and the launch of TCP/IP?
- **Category:** `multi_evidence`
- **Status:** **PASS**
- **Answer:** Between the inception of ARPANET in 1969 and the adoption of TCP/IP in 1983, the key milestones included Ray Tomlinson sending the first email and introducing the @ symbol in 1971, and the expansion of ARPANET to include international nodes in England and Norway by 1973.
- **Evidence:**
  - `[history_of_internet.txt]` "In 1971, Ray Tomlinson sent the first email over ARPANET and introduced the @ symbol to separate user names from computer names. By 1973, ARPANET had expanded to include nodes in England and Norway, making it the first international network."

## 3. Discussion of Limitations

1. **Table Structure Preservation**: While `pypdf` extracts raw text from PDF tables reliably, highly complex multi-row merged header tables lose strict 2D visual cell relationships when flattened to linear character streams. For specialized financial tables, vision-based layout models (LayoutLM) or native markdown tables provide higher fidelity.
2. **Embedded Diagram / Visual Data**: Standard text parsing ignores raster images, flowcharts, and embedded figures within PDFs. An end-to-end multimodal pipeline (e.g. Gemini Multimodal / ColPali) is required to index diagrams and chart graphics.
3. **Bi-Encoder Vector Limitations**: Bi-encoders (`all-MiniLM-L6-v2`) embed queries and chunks independently. For extremely broad questions spanning entire books, lead-chunk prior routing helps, but hierarchical summarization trees (RAPTOR) are required for full-book synthesis.
4. **Embedded Vector Database Scalability**: Embedded ChromaDB is optimized for single-instance deployments (<500k chunks). Enterprise environments with distributed horizontal replicas require managed distributed vector stores such as Qdrant, Milvus, or PostgreSQL with `pgvector`.
# Inverted Index Project

**Ajla Šačić**  

## Table of Contents

- [Project Description](#project-description)
  - [Stages](#stages)
    1. [Document Cleaning](#1-document-cleaning)
    2. [Document Merging](#2-document-merging)
    3. [MapReduce for Word Counts](#3-mapreduce-for-word-counts)
    4. [Creating the Inverted Index](#4-creating-the-inverted-index)
    5. [Searching the Inverted Index](#5-searching-the-inverted-index)
- [How to Run the Project](#how-to-run-the-project)
  - [Prerequisites](#prerequisites)
  - [Running the Search](#running-the-search)
  - [Running the Project From Scratch](#running-the-project-from-scratch)
    1. [Create a Virtual Environment](#1-create-a-virtual-environment)
    2. [Install Dependencies](#2-install-dependencies)
    3. [Run the Inverted Index Pipeline](#3-run-the-inverted-index-pipeline)
       - [3.1 Clean the Documents](#31-clean-the-documents)
       - [3.2 Combine the Files](#32-combine-the-files)
       - [3.3 Run the MapReduce](#33-run-the-mapreduce)
       - [3.4 Create the Inverted Index](#34-create-the-inverted-index)
       - [3.5 Get the Number of Words in Each File](#35-get-the-number-of-words-in-each-file)

## Project Description

The **Inverted Index Project** is designed to process a large set of documents and create an efficient search mechanism using an inverted index. The project is divided into several stages to ensure modularity, error checking, and ease of maintenance.

### Stages

1. **Document Cleaning**
2. **Document Merging**
3. **MapReduce to Get Word Counts**
4. **Creating the Inverted Index**
5. **Searching the Inverted Index**

#### 1. Document Cleaning

This stage involves preprocessing the raw documents to remove unwanted elements and prepare them for analysis. The cleaning process includes:

- **Removing Subtitles**: Text surrounded by `=` symbols.
- **Removing Wikitables**: Tables used in wiki markup.
- **Removing References and 'See Also' Sections**: These sections often contain non-essential information.
- **Removing HTML and XML Tags**: Stripping any embedded markup.
- **Separating Punctuation**: Ensuring punctuation is separated from words for accurate tokenization.

#### 2. Document Merging

Combining all cleaned documents into a single file for streamlined processing. The merged file is formatted as:


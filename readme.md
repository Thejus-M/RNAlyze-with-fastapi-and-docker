# RNAlyse: A   Machine Learning Based Approch for RNA Sequence Analysis and Classification 🧬 🧪 💻

This repository contains the code and data for a project aimed at finding whether a given DNA sequence is coding RNA or non-coding RNA using machine learning models. The project uses various features of the DNA sequence to train the models. 

# TODO

- [ ] Create Login and Signup
- [ ] Create Database for storing inputed value
- [ ] Create API calls
- [ ] Display graphs for each input
- [ ] Show history
- [ ] upload fasta file option

# Features 🔍
-  ORF length
	* T0
	* T1
	* T2
	* T3
-  ORF Ratio
-  Transcript Length
-  GC Content
-  Aromaticity
-  Isoelectric Point
-  Relative Codon Bias
-  Stop Codon Frequency
-  Molecular Weight
-  CpG Islands
-  Instability Index
-  Fickett Score
-  Gravy

# Dataset 📊

The data set used in this study consisted of both coding and long non-coding RNA sequences from the Homo Sapiens species and the Mus Musculus species. The coding RNA and  noncoding RNA sequences are downloaded from GENCODE  and NONCODE  databases.. The sequences are in FASTA format and have been pre-processed to extract various features such as ORF length, protein coding potential, etc. The dataset is split into training and testing sets, with 80% of the data used for training and the remaining 20% used for testing.

# Models 🤖

The following machine learning models have been implemented for this project:

-    Logistic Regression
-    Support Vector Machine (SVM)
-    Naive Bayes
-    Random Forest

These models have been trained using the features extracted from the dataset and are used to predict whether a given DNA sequence is coding RNA or non-coding RNA.

# Requirements 🛠️

To run the code in this repository, you will need:

-    Python 3.x
-    NumPy
-    Pandas
-    Scikit-learn
-    Matplotlib
-    Biopython
-    Fastapi

# Usage 🚀

To run the code in the provided repository, there are two methods: using Docker or from source.

#### Using Docker

1. Pull the Docker image using the following command:

	`docker pull iamfoss/rnalyze-server:v1`

2. Run the Docker container using the following command:

	`docker run --name server -p 8080:80 iamfoss/rnalyze-server:v1`

#### From source

1. Clone the repository using the following command:

	`git clone https://github.com/Thejus-M/RNAlyze-with-fastapi-and-docker.git`

2. Install the required dependencies using the following command:

	`pip install -r requirement.txt`

3. Run the application using the following command:

	```
	uvicorn src.main:app --reload
	```

These commands will start the FastAPI application and make it available on http://localhost:8080/ For more information on how to use FastAPI with Docker, you can refer to the official documentation[

# Conclusion 📝

This project shows that machine learning models can be used to accurately classify DNA sequences as coding or non-coding RNA based on various features. The models implemented in this project can be further optimized and used in various biological applications, such as identifying potential drug targets and understanding gene expression. So, let's go and explore the world of RNA with Machine Learning! 


#!/usr/bin/env python3
"""
Demo: Automated Library Creation

Simple demonstration of how to create libraries, documents, and chunks 
using the StackAI Vector Database API.

Topic: Machine Learning Fundamentals
- Clean, educational example
- Shows API usage patterns
- KISS approach - no complex processing

Usage:
    python demo_library_creation.py
"""

import asyncio
import aiohttp
import json
from typing import List, Dict, Any
from datetime import datetime


class StackAIClient:
    """Simple API client for StackAI Vector Database."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def create_library(self, name: str, description: str) -> Dict[str, Any]:
        """Create a new library."""
        payload = {
            "name": name,
            "description": description
        }
        async with self.session.post(f"{self.base_url}/api/v1/libraries/", json=payload) as resp:
            if resp.status != 201:
                error_text = await resp.text()
                raise Exception(f"Library creation failed (status {resp.status}): {error_text}")
            return await resp.json()
    
    async def create_document(self, library_id: str, name: str, content: str) -> Dict[str, Any]:
        """Create a new document."""
        payload = {
            "library_id": library_id,
            "name": name,
            "content": content,
            "content_type": "text/plain"
        }
        async with self.session.post(f"{self.base_url}/api/v1/documents/", json=payload) as resp:
            if resp.status != 201:
                error_text = await resp.text()
                raise Exception(f"Document creation failed (status {resp.status}): {error_text}")
            return await resp.json()
    
    async def create_chunk(self, document_id: str, library_id: str, text: str, position: int) -> Dict[str, Any]:
        """Create a single chunk."""
        payload = {
            "document_id": document_id,
            "library_id": library_id,
            "text": text,
            "position": position,
            "metadata": {"chunk_type": "content", "length": str(len(text))}
        }
        async with self.session.post(f"{self.base_url}/api/v1/chunks/", json=payload) as resp:
            if resp.status != 201:
                error_text = await resp.text()
                raise Exception(f"Chunk creation failed (status {resp.status}): {error_text}")
            return await resp.json()
    
    async def create_chunks_for_document(self, document_id: str, library_id: str, chunks: List[str]) -> List[Dict[str, Any]]:
        """Create multiple chunks for a document (one by one - KISS approach)."""
        created_chunks = []
        for i, text in enumerate(chunks):
            chunk = await self.create_chunk(document_id, library_id, text, i)
            created_chunks.append(chunk)
        return created_chunks


# Sample content: Machine Learning Fundamentals
ML_DOCUMENTS = {
    "Supervised Learning Basics": [
        "Supervised learning is a machine learning paradigm where algorithms learn from labeled training data.",
        "The goal is to map input features to correct output labels based on training examples.",
        "Common supervised learning tasks include classification and regression problems.",
        "Classification predicts discrete categories or classes for input data.",
        "Regression predicts continuous numerical values based on input features.",
        "Training data consists of input-output pairs that guide the learning process.",
        "Popular algorithms include linear regression, decision trees, and random forests.",
        "Cross-validation helps evaluate model performance on unseen data.",
        "Overfitting occurs when models memorize training data rather than learning patterns.",
        "Feature engineering involves selecting and transforming relevant input variables.",
        "Model evaluation uses metrics like accuracy, precision, recall, and F1-score.",
        "Hyperparameter tuning optimizes algorithm settings for better performance."
    ],
    
    "Neural Networks Introduction": [
        "Neural networks are computing systems inspired by biological neural networks.",
        "They consist of interconnected nodes called neurons organized in layers.",
        "The input layer receives data, hidden layers process it, and output layer produces results.",
        "Each connection has a weight that determines the strength of the signal.",
        "Activation functions introduce non-linearity, enabling complex pattern recognition.",
        "Forward propagation passes data through the network to generate predictions.",
        "Backpropagation calculates errors and updates weights to improve performance.",
        "Deep learning uses neural networks with multiple hidden layers.",
        "Convolutional neural networks excel at image recognition tasks.",
        "Recurrent neural networks handle sequential data like text and time series.",
        "Training requires large datasets and significant computational resources.",
        "Modern frameworks like TensorFlow and PyTorch simplify neural network development."
    ],
    
    "Data Preprocessing Essentials": [
        "Data preprocessing is the crucial first step in any machine learning pipeline.",
        "Raw data often contains missing values, outliers, and inconsistent formats.",
        "Data cleaning involves identifying and correcting errors in the dataset.",
        "Missing value imputation replaces absent data with reasonable estimates.",
        "Outlier detection identifies data points that deviate significantly from patterns.",
        "Feature scaling normalizes different variables to comparable ranges.",
        "Categorical encoding converts text categories into numerical representations.",
        "Data splitting divides datasets into training, validation, and test sets.",
        "Feature selection identifies the most relevant variables for the model.",
        "Dimensionality reduction techniques like PCA reduce feature complexity.",
        "Data augmentation artificially increases dataset size through transformations.",
        "Quality preprocessing significantly impacts final model performance."
    ]
}


async def create_ml_library_demo():
    """Create a complete ML fundamentals library with documents and chunks."""
    
    # Add timestamp for uniqueness
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    library_name = f"Machine Learning Fundamentals {timestamp}"
    
    print(f"🚀 Creating {library_name}")
    print("=" * 60)
    
    async with StackAIClient() as client:
        # Create library
        print("📚 Creating library...")
        library = await client.create_library(
            name=library_name,
            description="Essential concepts and techniques in machine learning for beginners and practitioners."
        )
        library_id = library["id"]
        print(f"✅ Library created: {library['name']} (ID: {library_id})")
        
        # Create documents and chunks
        total_chunks = 0
        for doc_name, chunks_text in ML_DOCUMENTS.items():
            print(f"\n📄 Creating document: {doc_name}")
            
            # Create document
            document = await client.create_document(
                library_id=library_id,
                name=doc_name,
                content=" ".join(chunks_text)  # Full content
            )
            document_id = document["id"]
            
            # Create chunks
            chunks_result = await client.create_chunks_for_document(
                document_id=document_id,
                library_id=library_id,
                chunks=chunks_text
            )
            
            chunk_count = len(chunks_result)
            total_chunks += chunk_count
            print(f"  ✅ Created {chunk_count} chunks")
        
        print(f"\n🎉 Demo completed successfully!")
        print(f"📊 Summary:")
        print(f"   - Library: {library['name']}")
        print(f"   - Documents: {len(ML_DOCUMENTS)}")
        print(f"   - Total chunks: {total_chunks}")
        print(f"   - Average chunks per document: {total_chunks // len(ML_DOCUMENTS)}")
        
        return library_id


async def test_search_demo(library_id: str):
    """Quick search test on the created library."""
    print(f"\n🔍 Testing search functionality...")
    
    async with StackAIClient() as client:
        # Test search
        search_payload = {
            "query": "What is supervised learning?",
            "library_id": library_id,
            "k": 3
        }
        
        async with client.session.post(
            f"{client.base_url}/api/v1/search/", 
            json=search_payload
        ) as resp:
            results = await resp.json()
        
        print(f"✅ Search returned {len(results.get('results', []))} results")
        print(f"🔧 Algorithm used: {results.get('algorithm_used', 'unknown')}")
        
        # Show first result
        if results.get('results'):
            first_result = results['results'][0]
            print(f"📝 Top result (similarity: {first_result['similarity_score']:.3f}):")
            print(f"   {first_result['text'][:100]}...")


async def main():
    """Main demo function."""
    try:
        # Create the library
        library_id = await create_ml_library_demo()
        
        # Test search
        await test_search_demo(library_id)
        
        print(f"\n✨ Demo complete! Library ID: {library_id}")
        print(f"🌐 You can now test the API at: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("💡 Make sure the API server is running on http://localhost:8000")


if __name__ == "__main__":
    asyncio.run(main()) 
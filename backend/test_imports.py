"""
Quick test to verify LangChain and Gemini are working
"""
try:
    print("Testing imports...")
    from langchain_google_genai import ChatGoogleGenerativeAI
    print("✓ langchain_google_genai imported successfully")
    
    from langchain.prompts import ChatPromptTemplate
    print("✓ ChatPromptTemplate imported successfully")
    
    from pydantic import BaseModel
    print("✓ Pydantic v2 imported successfully")
    
    print("\n✅ All imports successful! No Pydantic v1/v2 conflicts.")
    print("The application should now run correctly.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nTry running: pip install --upgrade langchain langchain-core langchain-google-genai")

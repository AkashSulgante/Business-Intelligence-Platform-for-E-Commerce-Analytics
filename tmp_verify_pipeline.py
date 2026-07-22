import os
import sys
os.chdir(r'c:\Users\akash\Downloads\Telegram Desktop\projects\GOOGLE ANALYTICS PRO\ecommerce_bi_platform')
sys.path.insert(0, os.getcwd())
import etl.pipeline as pipeline
print(pipeline.run_pipeline())

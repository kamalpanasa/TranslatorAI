import os
from typing import Callable, Coroutine, Any
import pandas as pd
from app.utils.logger import get_logger
from app.utils.exceptions import FileProcessingError

logger = get_logger("app.processing.csv_processor")


class CSVProcessor:
    @staticmethod
    async def translate_csv_file(
        input_path: str,
        output_path: str,
        translate_func: Callable[[str], Coroutine[Any, Any, str]]
    ) -> str:
        """
        Translates a CSV file:
        1. Open CSV using pandas.
        2. Identify object/string columns.
        3. Translate non-empty string values.
        4. Save to new CSV.
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"CSV file not found: {input_path}")

        try:
            logger.info(f"Opening CSV for translation: {input_path}")
            
            # Read CSV
            df = pd.read_csv(input_path)
            
            # Iterate columns
            for col in df.columns:
                # Only process string/object columns
                if df[col].dtype == object or df[col].dtype == 'string':
                    logger.info(f"Translating CSV column: {col}")
                    
                    # Convert to series list for simple async replacement
                    vals = df[col].tolist()
                    translated_vals = []
                    
                    for v in vals:
                        if pd.isna(v) or not isinstance(v, str):
                            translated_vals.append(v)
                        else:
                            clean_v = str(v).strip()
                            if clean_v:
                                trans = await translate_func(clean_v)
                                translated_vals.append(trans)
                            else:
                                translated_vals.append(v)
                                
                    df[col] = translated_vals

            # Save back to CSV
            df.to_csv(output_path, index=False)
            logger.info(f"Translated CSV saved successfully to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error processing CSV file: {str(e)}", exc_info=True)
            raise FileProcessingError(f"Failed to translate CSV file: {str(e)}")

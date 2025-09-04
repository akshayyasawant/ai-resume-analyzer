import pandas as pd
from typing import List, Dict
import io

class ExportUtils:
    
    @staticmethod
    def create_results_dataframe(results: List[Dict]) -> pd.DataFrame:
        """Convert results to pandas DataFrame for export"""
        if not results:
            return pd.DataFrame()
        
        export_data = []
        for result in results:
            export_data.append({
                'Rank': len(export_data) + 1,
                'Candidate_Name': result['filename'].replace('.pdf', ''),
                'Combined_Score': f"{result['combined_score']:.3f}",
                'Similarity_Score': f"{result['similarity_score']:.3f}",
                'Keyword_Match_Score': f"{result['keyword_score']:.3f}",
                'Experience_Score': f"{result['experience_score']:.3f}",
                'Years_Experience': result['experience_years'],
                'Skills_Found': ', '.join(result['skills_found'][:10]),  # Limit to first 10 skills
                'Matching_Keywords': ', '.join(result['matching_keywords'])
            })
        
        return pd.DataFrame(export_data)
    
    @staticmethod
    def export_to_excel(results: List[Dict], filename: str = "resume_rankings.xlsx") -> bytes:
        """Export results to Excel file"""
        df = ExportUtils.create_results_dataframe(results)
        
        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Resume Rankings', index=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Resume Rankings']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        return output.getvalue()
    
    @staticmethod
    def export_to_csv(results: List[Dict]) -> str:
        """Export results to CSV format"""
        df = ExportUtils.create_results_dataframe(results)
        return df.to_csv(index=False)

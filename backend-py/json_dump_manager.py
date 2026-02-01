"""
JSON Dump Manager for Scraped Data
Handles exporting, tracking, and managing scraped data dumps
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class JSONDumpManager:
    """Manages JSON dumps of scraped data with checklist tracking"""
    
    def __init__(self, dump_dir: str = "dumps"):
        """
        Initialize the JSON dump manager
        
        Args:
            dump_dir: Directory to store JSON dumps
        """
        self.dump_dir = dump_dir
        self.checklist_file = os.path.join(dump_dir, "_dump_checklist.json")
        self._ensure_dump_directory()
        self.checklist = self._load_checklist()
    
    def _ensure_dump_directory(self):
        """Create dump directory if it doesn't exist"""
        if not os.path.exists(self.dump_dir):
            os.makedirs(self.dump_dir)
            logger.info(f"Created dump directory: {self.dump_dir}")
    
    def _load_checklist(self) -> Dict[str, Any]:
        """Load the dump checklist from file"""
        if os.path.exists(self.checklist_file):
            try:
                with open(self.checklist_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading checklist: {e}")
                return {"dumps": [], "total_dumps": 0}
        return {"dumps": [], "total_dumps": 0}
    
    def _save_checklist(self):
        """Save the dump checklist to file"""
        try:
            with open(self.checklist_file, 'w', encoding='utf-8') as f:
                json.dump(self.checklist, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving checklist: {e}")
    
    def dump_data(
        self,
        data: Any,
        dump_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Dump data to JSON file with tracking
        
        Args:
            data: Data to dump (signals, financial data, etc.)
            dump_type: Type of dump (general, company, financial, etc.)
            metadata: Additional metadata about the dump
            filename: Optional custom filename
            
        Returns:
            Dictionary with dump information
        """
        timestamp = datetime.now().isoformat()
        
        # Generate filename if not provided
        if not filename:
            date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{dump_type}_{date_str}.json"
        
        filepath = os.path.join(self.dump_dir, filename)
        
        # Prepare dump data with metadata
        dump_content = {
            "dump_info": {
                "timestamp": timestamp,
                "dump_type": dump_type,
                "filename": filename,
                "metadata": metadata or {}
            },
            "data": data
        }
        
        # Write to file
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(dump_content, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully dumped data to: {filepath}")
            
            # Update checklist
            checklist_entry = {
                "id": len(self.checklist["dumps"]) + 1,
                "filename": filename,
                "filepath": filepath,
                "timestamp": timestamp,
                "dump_type": dump_type,
                "metadata": metadata or {},
                "size_bytes": os.path.getsize(filepath),
                "record_count": self._count_records(data)
            }
            
            self.checklist["dumps"].append(checklist_entry)
            self.checklist["total_dumps"] = len(self.checklist["dumps"])
            self.checklist["last_dump"] = timestamp
            self._save_checklist()
            
            return {
                "success": True,
                "filepath": filepath,
                "filename": filename,
                "checklist_entry": checklist_entry
            }
            
        except Exception as e:
            logger.error(f"Error dumping data: {e}")
            return {
                "success": False,
                "error": str(e),
                "filepath": filepath
            }
    
    def _count_records(self, data: Any) -> int:
        """Count the number of records in the data"""
        if isinstance(data, list):
            return len(data)
        elif isinstance(data, dict):
            # Check for common signal/data keys
            if "signals" in data:
                return len(data["signals"])
            elif "data" in data and isinstance(data["data"], list):
                return len(data["data"])
            return 1
        return 1
    
    def get_checklist(self) -> Dict[str, Any]:
        """Get the complete dump checklist"""
        return self.checklist
    
    def get_dump_by_id(self, dump_id: int) -> Optional[Dict[str, Any]]:
        """Get dump information by ID"""
        for dump in self.checklist["dumps"]:
            if dump["id"] == dump_id:
                return dump
        return None
    
    def get_dump_by_filename(self, filename: str) -> Optional[Dict[str, Any]]:
        """Get dump information by filename"""
        for dump in self.checklist["dumps"]:
            if dump["filename"] == filename:
                return dump
        return None
    
    def load_dump(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load a specific dump file"""
        filepath = os.path.join(self.dump_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading dump {filename}: {e}")
                return None
        return None
    
    def delete_dump(self, filename: str) -> bool:
        """Delete a dump file and update checklist"""
        filepath = os.path.join(self.dump_dir, filename)
        
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
            
            # Remove from checklist
            self.checklist["dumps"] = [
                d for d in self.checklist["dumps"] 
                if d["filename"] != filename
            ]
            self.checklist["total_dumps"] = len(self.checklist["dumps"])
            self._save_checklist()
            
            logger.info(f"Deleted dump: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting dump {filename}: {e}")
            return False
    
    def clear_all_dumps(self) -> bool:
        """Clear all dumps (use with caution)"""
        try:
            # Delete all dump files
            for dump in self.checklist["dumps"]:
                filepath = dump["filepath"]
                if os.path.exists(filepath):
                    os.remove(filepath)
            
            # Reset checklist
            self.checklist = {"dumps": [], "total_dumps": 0}
            self._save_checklist()
            
            logger.info("Cleared all dumps")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing dumps: {e}")
            return False
    
    def get_dumps_by_type(self, dump_type: str) -> List[Dict[str, Any]]:
        """Get all dumps of a specific type"""
        return [
            d for d in self.checklist["dumps"] 
            if d["dump_type"] == dump_type
        ]
    
    def get_dumps_by_date(self, date_str: str) -> List[Dict[str, Any]]:
        """Get all dumps from a specific date (YYYY-MM-DD)"""
        return [
            d for d in self.checklist["dumps"] 
            if d["timestamp"].startswith(date_str)
        ]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics of all dumps"""
        if not self.checklist["dumps"]:
            return {
                "total_dumps": 0,
                "total_records": 0,
                "total_size_mb": 0,
                "dumps_by_type": {},
                "oldest_dump": None,
                "newest_dump": None
            }
        
        dumps = self.checklist["dumps"]
        total_records = sum(d.get("record_count", 0) for d in dumps)
        total_size = sum(d.get("size_bytes", 0) for d in dumps)
        
        dumps_by_type = {}
        for dump in dumps:
            dtype = dump["dump_type"]
            dumps_by_type[dtype] = dumps_by_type.get(dtype, 0) + 1
        
        timestamps = [d["timestamp"] for d in dumps]
        
        return {
            "total_dumps": len(dumps),
            "total_records": total_records,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "dumps_by_type": dumps_by_type,
            "oldest_dump": min(timestamps),
            "newest_dump": max(timestamps)
        }

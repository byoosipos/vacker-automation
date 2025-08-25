# Evidence Validation System for Advanced AI Risk Assessment
# Copyright (c) 2025, Vacker and contributors

import frappe
import json
import re
import base64
import io
from datetime import datetime, timedelta
from frappe.utils import flt, getdate, add_days, nowdate, cstr
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import cv2
import numpy as np
import requests


class EvidenceValidationSystem:
    """
    Advanced Evidence Validation System with OCR and AI analysis
    Provides multi-modal evidence validation for accountability framework
    """
    
    def __init__(self, user=None, company=None):
        self.user = user or frappe.session.user
        self.company = company or frappe.defaults.get_user_default('Company')
        self.ocr_confidence_threshold = 0.7
        self.image_quality_threshold = 0.6
        
    def validate_evidence_submission(self, doctype, doc_name, evidence_files):
        """Main evidence validation method"""
        
        validation_result = {
            'overall_score': 0,
            'validation_status': 'pending',
            'evidence_analysis': [],
            'fraud_indicators': [],
            'recommendations': [],
            'authenticity_score': 0,
            'compliance_status': 'under_review'
        }
        
        total_evidence_score = 0
        evidence_count = 0
        
        for file_data in evidence_files:
            evidence_analysis = self.analyze_single_evidence(doctype, doc_name, file_data)
            validation_result['evidence_analysis'].append(evidence_analysis)
            
            total_evidence_score += evidence_analysis['quality_score']
            evidence_count += 1
            
            # Collect fraud indicators
            if evidence_analysis.get('fraud_indicators'):
                validation_result['fraud_indicators'].extend(evidence_analysis['fraud_indicators'])
        
        # Calculate overall scores
        if evidence_count > 0:
            validation_result['overall_score'] = total_evidence_score / evidence_count
            validation_result['authenticity_score'] = self.calculate_authenticity_score(validation_result)
        
        # Determine validation status
        validation_result['validation_status'] = self.determine_validation_status(validation_result)
        validation_result['compliance_status'] = self.determine_compliance_status(validation_result)
        
        # Generate recommendations
        validation_result['recommendations'] = self.generate_evidence_recommendations(validation_result)
        
        return validation_result
    
    def analyze_single_evidence(self, doctype, doc_name, file_data):
        """Analyze a single piece of evidence"""
        
        analysis_result = {
            'file_name': file_data.get('file_name', 'unknown'),
            'file_type': file_data.get('file_type', 'unknown'),
            'quality_score': 0,
            'ocr_results': {},
            'image_analysis': {},
            'fraud_indicators': [],
            'authenticity_factors': [],
            'extracted_data': {}
        }
        
        try:
            file_content = self.get_file_content(file_data)
            
            if self.is_image_file(file_data['file_name']):
                # Image processing and OCR
                image_analysis = self.analyze_image_evidence(file_content)
                analysis_result.update(image_analysis)
                
                # OCR processing
                if image_analysis['is_receipt_like']:
                    ocr_results = self.perform_ocr_analysis(file_content, doctype)
                    analysis_result['ocr_results'] = ocr_results
                    analysis_result['extracted_data'] = ocr_results.get('extracted_data', {})
            
            elif self.is_pdf_file(file_data['file_name']):
                # PDF processing
                pdf_analysis = self.analyze_pdf_evidence(file_content)
                analysis_result.update(pdf_analysis)
            
            # Fraud detection
            fraud_indicators = self.detect_evidence_fraud(analysis_result)
            analysis_result['fraud_indicators'] = fraud_indicators
            
            # Calculate quality score
            analysis_result['quality_score'] = self.calculate_evidence_quality_score(analysis_result)
            
        except Exception as e:
            frappe.log_error(f"Evidence Analysis Error: {str(e)}", "Evidence Validation")
            analysis_result['error'] = str(e)
            analysis_result['quality_score'] = 0
        
        return analysis_result
    
    def analyze_image_evidence(self, image_content):
        """Analyze image evidence for quality and authenticity"""
        
        analysis = {
            'image_quality': 0,
            'is_receipt_like': False,
            'resolution': (0, 0),
            'clarity_score': 0,
            'lighting_score': 0,
            'authenticity_indicators': []
        }
        
        try:
            # Load image
            image = Image.open(io.BytesIO(image_content))
            analysis['resolution'] = image.size
            
            # Convert to OpenCV format for advanced analysis
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Image quality analysis
            analysis['clarity_score'] = self.assess_image_clarity(cv_image)
            analysis['lighting_score'] = self.assess_lighting_quality(cv_image)
            
            # Receipt detection
            analysis['is_receipt_like'] = self.detect_receipt_characteristics(cv_image)
            
            # Digital manipulation detection
            manipulation_indicators = self.detect_digital_manipulation(cv_image)
            analysis['authenticity_indicators'] = manipulation_indicators
            
            # Overall image quality score
            analysis['image_quality'] = (
                analysis['clarity_score'] * 0.4 +
                analysis['lighting_score'] * 0.3 +
                (1.0 if analysis['is_receipt_like'] else 0.5) * 0.3
            )
            
        except Exception as e:
            frappe.log_error(f"Image Analysis Error: {str(e)}", "Evidence Validation")
            analysis['error'] = str(e)
        
        return analysis
    
    def perform_ocr_analysis(self, image_content, doctype):
        """Perform OCR analysis on receipt images"""
        
        ocr_results = {
            'raw_text': '',
            'confidence_score': 0,
            'extracted_data': {},
            'validation_status': 'pending',
            'business_validation': {}
        }
        
        try:
            # Preprocess image for better OCR
            processed_image = self.preprocess_image_for_ocr(image_content)
            
            # Perform OCR with confidence scores
            ocr_data = pytesseract.image_to_data(processed_image, output_type=pytesseract.Output.DICT)
            
            # Extract text and calculate confidence
            text_blocks = []
            confidences = []
            
            for i, text in enumerate(ocr_data['text']):
                if text.strip():
                    text_blocks.append(text)
                    confidences.append(ocr_data['conf'][i])
            
            ocr_results['raw_text'] = ' '.join(text_blocks)
            ocr_results['confidence_score'] = np.mean([c for c in confidences if c > 0]) / 100 if confidences else 0
            
            # Extract structured data from receipt
            if doctype in ['Expense Claim', 'Material Request']:
                structured_data = self.extract_receipt_data(ocr_results['raw_text'])
                ocr_results['extracted_data'] = structured_data
                
                # Business validation
                business_validation = self.validate_receipt_business_logic(structured_data, doctype)
                ocr_results['business_validation'] = business_validation
            
            # Determine validation status
            if ocr_results['confidence_score'] >= self.ocr_confidence_threshold:
                ocr_results['validation_status'] = 'valid'
            elif ocr_results['confidence_score'] >= 0.5:
                ocr_results['validation_status'] = 'requires_review'
            else:
                ocr_results['validation_status'] = 'invalid'
                
        except Exception as e:
            frappe.log_error(f"OCR Analysis Error: {str(e)}", "Evidence Validation")
            ocr_results['error'] = str(e)
        
        return ocr_results
    
    def extract_receipt_data(self, ocr_text):
        """Extract structured data from OCR text"""
        
        extracted_data = {
            'vendor_name': '',
            'receipt_number': '',
            'date': '',
            'total_amount': 0,
            'items': [],
            'tax_amount': 0,
            'currency': 'UGX',
            'contact_info': {}
        }
        
        try:
            text_lines = ocr_text.split('\n')
            
            # Extract vendor name (usually first few lines)
            for i, line in enumerate(text_lines[:5]):
                if re.search(r'[A-Za-z]{3,}', line) and not re.search(r'\d{4}', line):
                    extracted_data['vendor_name'] = line.strip()
                    break
            
            # Extract receipt number
            receipt_patterns = [
                r'receipt[\s#:]*(\d+)',
                r'invoice[\s#:]*(\d+)',
                r'ref[\s#:]*(\d+)',
                r'no[\s#:]*(\d+)'
            ]
            
            for pattern in receipt_patterns:
                match = re.search(pattern, ocr_text, re.IGNORECASE)
                if match:
                    extracted_data['receipt_number'] = match.group(1)
                    break
            
            # Extract date
            date_patterns = [
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'(\d{1,2}\s+[A-Za-z]{3,}\s+\d{2,4})',
                r'(\d{2,4}[/-]\d{1,2}[/-]\d{1,2})'
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, ocr_text)
                if match:
                    extracted_data['date'] = match.group(1)
                    break
            
            # Extract total amount
            amount_patterns = [
                r'total[\s:]*ugx[\s]*(\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'total[\s:]*(\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'amount[\s:]*ugx[\s]*(\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*ugx'
            ]
            
            for pattern in amount_patterns:
                match = re.search(pattern, ocr_text, re.IGNORECASE)
                if match:
                    amount_str = match.group(1).replace(',', '')
                    extracted_data['total_amount'] = flt(amount_str)
                    break
            
            # Extract tax amount
            tax_patterns = [
                r'vat[\s:]*(\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'tax[\s:]*(\d+(?:,\d{3})*(?:\.\d{2})?)'
            ]
            
            for pattern in tax_patterns:
                match = re.search(pattern, ocr_text, re.IGNORECASE)
                if match:
                    tax_str = match.group(1).replace(',', '')
                    extracted_data['tax_amount'] = flt(tax_str)
                    break
            
            # Extract contact information
            phone_match = re.search(r'(\+?256\d{9}|\d{10})', ocr_text)
            if phone_match:
                extracted_data['contact_info']['phone'] = phone_match.group(1)
            
            email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', ocr_text)
            if email_match:
                extracted_data['contact_info']['email'] = email_match.group(1)
            
        except Exception as e:
            frappe.log_error(f"Data Extraction Error: {str(e)}", "Evidence Validation")
        
        return extracted_data
    
    def validate_receipt_business_logic(self, extracted_data, doctype):
        """Validate receipt data against business logic"""
        
        validation = {
            'amount_validation': 'pending',
            'date_validation': 'pending',
            'vendor_validation': 'pending',
            'completeness_score': 0,
            'business_rules_compliance': []
        }
        
        # Completeness validation
        required_fields = ['vendor_name', 'total_amount', 'date']
        complete_fields = sum(1 for field in required_fields if extracted_data.get(field))
        validation['completeness_score'] = complete_fields / len(required_fields)
        
        # Amount validation
        if extracted_data.get('total_amount', 0) > 0:
            if extracted_data['total_amount'] <= 10000000:  # 10M UGX reasonable limit
                validation['amount_validation'] = 'valid'
            else:
                validation['amount_validation'] = 'suspicious_amount'
        else:
            validation['amount_validation'] = 'missing_amount'
        
        # Date validation
        if extracted_data.get('date'):
            try:
                # Parse date and check if reasonable
                parsed_date = self.parse_extracted_date(extracted_data['date'])
                days_diff = (getdate(nowdate()) - parsed_date).days
                
                if 0 <= days_diff <= 90:  # Within last 90 days
                    validation['date_validation'] = 'valid'
                elif days_diff > 90:
                    validation['date_validation'] = 'old_receipt'
                else:
                    validation['date_validation'] = 'future_date'
            except:
                validation['date_validation'] = 'invalid_date_format'
        else:
            validation['date_validation'] = 'missing_date'
        
        # Vendor validation
        if extracted_data.get('vendor_name'):
            # Check if vendor exists in system
            vendor_exists = frappe.db.exists('Supplier', {'supplier_name': extracted_data['vendor_name']})
            validation['vendor_validation'] = 'known_vendor' if vendor_exists else 'unknown_vendor'
        else:
            validation['vendor_validation'] = 'missing_vendor'
        
        return validation
    
    def detect_evidence_fraud(self, evidence_analysis):
        """Detect potential fraud indicators in evidence"""
        
        fraud_indicators = []
        
        # Image-based fraud indicators
        if evidence_analysis.get('image_analysis'):
            image_data = evidence_analysis['image_analysis']
            
            # Low image quality (potential sign of screenshot or manipulation)
            if image_data.get('clarity_score', 0) < 0.4:
                fraud_indicators.append({
                    'type': 'poor_image_quality',
                    'severity': 'medium',
                    'description': 'Image quality too low - possible screenshot or manipulation'
                })
            
            # Digital manipulation indicators
            if image_data.get('authenticity_indicators'):
                for indicator in image_data['authenticity_indicators']:
                    if indicator['suspicious']:
                        fraud_indicators.append({
                            'type': 'digital_manipulation',
                            'severity': 'high',
                            'description': f"Digital manipulation detected: {indicator['type']}"
                        })
        
        # OCR-based fraud indicators
        if evidence_analysis.get('ocr_results'):
            ocr_data = evidence_analysis['ocr_results']
            
            # Inconsistent formatting
            if ocr_data.get('extracted_data'):
                extracted = ocr_data['extracted_data']
                
                # Round number amounts (suspicious pattern)
                if extracted.get('total_amount', 0) > 0:
                    amount = extracted['total_amount']
                    if amount >= 10000 and amount % 10000 == 0:
                        fraud_indicators.append({
                            'type': 'round_amount',
                            'severity': 'medium',
                            'description': f'Suspiciously round amount: {amount:,.0f} UGX'
                        })
                
                # Missing critical information
                if not extracted.get('vendor_name'):
                    fraud_indicators.append({
                        'type': 'missing_vendor',
                        'severity': 'high',
                        'description': 'Receipt missing vendor information'
                    })
                
                # Duplicate receipt detection
                if self.check_duplicate_receipt(extracted):
                    fraud_indicators.append({
                        'type': 'duplicate_receipt',
                        'severity': 'high',
                        'description': 'Receipt appears to be a duplicate'
                    })
        
        return fraud_indicators
    
    def calculate_evidence_quality_score(self, analysis_result):
        """Calculate overall quality score for evidence"""
        
        quality_factors = []
        
        # Image quality factor
        if analysis_result.get('image_analysis'):
            image_quality = analysis_result['image_analysis'].get('image_quality', 0)
            quality_factors.append(('image_quality', image_quality, 0.3))
        
        # OCR confidence factor
        if analysis_result.get('ocr_results'):
            ocr_confidence = analysis_result['ocr_results'].get('confidence_score', 0)
            quality_factors.append(('ocr_confidence', ocr_confidence, 0.3))
            
            # Business validation factor
            if analysis_result['ocr_results'].get('business_validation'):
                business_val = analysis_result['ocr_results']['business_validation']
                completeness = business_val.get('completeness_score', 0)
                quality_factors.append(('completeness', completeness, 0.2))
        
        # Fraud indicators penalty
        fraud_count = len(analysis_result.get('fraud_indicators', []))
        fraud_penalty = max(0, 1 - (fraud_count * 0.2))
        quality_factors.append(('fraud_penalty', fraud_penalty, 0.2))
        
        # Calculate weighted average
        if quality_factors:
            total_weight = sum(weight for _, _, weight in quality_factors)
            weighted_score = sum(score * weight for _, score, weight in quality_factors) / total_weight
            return weighted_score
        
        return 0
    
    def calculate_authenticity_score(self, validation_result):
        """Calculate overall authenticity score"""
        
        if not validation_result['evidence_analysis']:
            return 0
        
        authenticity_factors = []
        
        for evidence in validation_result['evidence_analysis']:
            # Base score from quality
            base_score = evidence.get('quality_score', 0)
            
            # Fraud penalty
            fraud_count = len(evidence.get('fraud_indicators', []))
            high_severity_fraud = sum(1 for fi in evidence.get('fraud_indicators', []) 
                                    if fi.get('severity') == 'high')
            
            fraud_penalty = max(0, 1 - (fraud_count * 0.1) - (high_severity_fraud * 0.2))
            
            authenticity_score = base_score * fraud_penalty
            authenticity_factors.append(authenticity_score)
        
        return sum(authenticity_factors) / len(authenticity_factors) if authenticity_factors else 0
    
    def determine_validation_status(self, validation_result):
        """Determine overall validation status"""
        
        if validation_result['overall_score'] >= 0.8 and validation_result['authenticity_score'] >= 0.7:
            return 'approved'
        elif validation_result['overall_score'] >= 0.6 and validation_result['authenticity_score'] >= 0.5:
            return 'requires_review'
        else:
            return 'rejected'
    
    def determine_compliance_status(self, validation_result):
        """Determine compliance status"""
        
        high_risk_fraud = any(fi.get('severity') == 'high' 
                             for evidence in validation_result['evidence_analysis']
                             for fi in evidence.get('fraud_indicators', []))
        
        if high_risk_fraud:
            return 'non_compliant'
        elif validation_result['validation_status'] == 'approved':
            return 'compliant'
        else:
            return 'under_review'
    
    def generate_evidence_recommendations(self, validation_result):
        """Generate recommendations for evidence improvement"""
        
        recommendations = []
        
        # Overall score recommendations
        if validation_result['overall_score'] < 0.6:
            recommendations.append("Evidence quality below acceptable standards - provide clearer documentation")
        
        # Fraud indicators recommendations
        if validation_result['fraud_indicators']:
            high_risk_fraud = [fi for fi in validation_result['fraud_indicators'] if fi.get('severity') == 'high']
            if high_risk_fraud:
                recommendations.append("Critical fraud indicators detected - provide alternative evidence")
        
        # Individual evidence recommendations
        for evidence in validation_result['evidence_analysis']:
            if evidence.get('quality_score', 0) < 0.5:
                recommendations.append(f"Improve quality of {evidence.get('file_name', 'evidence file')}")
            
            if evidence.get('ocr_results', {}).get('confidence_score', 0) < 0.6:
                recommendations.append("Provide clearer receipt images for better text recognition")
        
        # Business validation recommendations
        for evidence in validation_result['evidence_analysis']:
            business_val = evidence.get('ocr_results', {}).get('business_validation', {})
            
            if business_val.get('completeness_score', 0) < 0.8:
                recommendations.append("Ensure receipt contains all required information (vendor, amount, date)")
            
            if business_val.get('vendor_validation') == 'unknown_vendor':
                recommendations.append("Verify vendor information - vendor not found in system")
        
        return recommendations
    
    # Helper methods
    
    def get_file_content(self, file_data):
        """Get file content from various sources"""
        if 'content' in file_data:
            return base64.b64decode(file_data['content'])
        elif 'file_url' in file_data:
            # Download file content
            response = requests.get(file_data['file_url'])
            return response.content
        else:
            raise ValueError("No file content or URL provided")
    
    def is_image_file(self, filename):
        """Check if file is an image"""
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']
        return any(filename.lower().endswith(ext) for ext in image_extensions)
    
    def is_pdf_file(self, filename):
        """Check if file is a PDF"""
        return filename.lower().endswith('.pdf')
    
    def preprocess_image_for_ocr(self, image_content):
        """Preprocess image for better OCR results"""
        
        # Load image
        image = Image.open(io.BytesIO(image_content))
        
        # Convert to grayscale
        image = image.convert('L')
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.5)
        
        # Apply noise reduction
        image = image.filter(ImageFilter.MedianFilter(size=3))
        
        return image
    
    def assess_image_clarity(self, cv_image):
        """Assess image clarity using Laplacian variance"""
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Normalize to 0-1 scale (empirically determined thresholds)
        clarity_score = min(laplacian_var / 1000, 1.0)
        return clarity_score
    
    def assess_lighting_quality(self, cv_image):
        """Assess lighting quality"""
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # Calculate histogram
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        
        # Check for good distribution (not too dark or too bright)
        total_pixels = gray.shape[0] * gray.shape[1]
        dark_pixels = np.sum(hist[:50]) / total_pixels
        bright_pixels = np.sum(hist[200:]) / total_pixels
        
        # Good lighting has balanced distribution
        lighting_score = 1.0 - max(dark_pixels, bright_pixels)
        return max(lighting_score, 0.0)
    
    def detect_receipt_characteristics(self, cv_image):
        """Detect if image looks like a receipt"""
        
        # Convert to grayscale
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # Detect horizontal lines (common in receipts)
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        horizontal_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, horizontal_kernel)
        
        # Count horizontal lines
        line_count = cv2.countNonZero(horizontal_lines)
        
        # Check aspect ratio (receipts are typically tall and narrow)
        height, width = gray.shape
        aspect_ratio = height / width
        
        # Receipt-like characteristics
        has_lines = line_count > (height * 0.1)  # At least 10% of height in lines
        good_aspect_ratio = aspect_ratio > 1.2  # Taller than wide
        
        return has_lines and good_aspect_ratio
    
    def detect_digital_manipulation(self, cv_image):
        """Detect signs of digital manipulation"""
        
        indicators = []
        
        # Check for JPEG compression artifacts
        if self.has_unusual_compression_artifacts(cv_image):
            indicators.append({
                'type': 'compression_artifacts',
                'suspicious': True,
                'description': 'Unusual JPEG compression patterns detected'
            })
        
        # Check for copy-paste patterns
        if self.detect_copy_paste_patterns(cv_image):
            indicators.append({
                'type': 'copy_paste',
                'suspicious': True,
                'description': 'Potential copy-paste manipulation detected'
            })
        
        return indicators
    
    def has_unusual_compression_artifacts(self, cv_image):
        """Simplified compression artifact detection"""
        # This is a simplified version - would need more sophisticated analysis
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # Look for unusual noise patterns
        noise = cv2.medianBlur(gray, 5)
        diff = cv2.absdiff(gray, noise)
        
        # High noise could indicate compression manipulation
        noise_level = np.mean(diff)
        return noise_level > 15  # Empirical threshold
    
    def detect_copy_paste_patterns(self, cv_image):
        """Simplified copy-paste detection"""
        # This is a simplified version - would need more sophisticated analysis
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # Look for repeated patterns using template matching
        # This is a basic implementation
        template_size = min(gray.shape[0] // 10, gray.shape[1] // 10, 50)
        
        if template_size < 10:
            return False
        
        # Take a template from one corner
        template = gray[:template_size, :template_size]
        
        # Search for matches
        result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= 0.8)
        
        # If we find multiple high-confidence matches, it might be copy-paste
        return len(locations[0]) > 3
    
    def check_duplicate_receipt(self, extracted_data):
        """Check if receipt data matches existing records"""
        
        if not extracted_data.get('total_amount') or not extracted_data.get('vendor_name'):
            return False
        
        # Search for similar receipts in expense claims
        similar_receipts = frappe.db.sql("""
            SELECT COUNT(*) as count
            FROM `tabExpense Claim Detail` ecd
            JOIN `tabExpense Claim` ec ON ecd.parent = ec.name
            WHERE ecd.amount = %s
            AND ec.docstatus = 1
            AND ec.creation >= %s
        """, (extracted_data['total_amount'], add_days(nowdate(), -90)), as_dict=True)
        
        return similar_receipts[0]['count'] > 0 if similar_receipts else False
    
    def parse_extracted_date(self, date_string):
        """Parse extracted date string"""
        
        # Common date formats
        date_formats = [
            '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d',
            '%d/%m/%y', '%d-%m-%y', '%y-%m-%d',
            '%d %B %Y', '%d %b %Y'
        ]
        
        for date_format in date_formats:
            try:
                return datetime.strptime(date_string, date_format).date()
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse date: {date_string}")


# Frappe whitelisted methods

@frappe.whitelist()
def validate_evidence_files(doctype, doc_name, evidence_files_json):
    """API method for evidence validation"""
    try:
        evidence_files = json.loads(evidence_files_json)
        validator = EvidenceValidationSystem()
        return validator.validate_evidence_submission(doctype, doc_name, evidence_files)
    except Exception as e:
        frappe.log_error(f"Evidence Validation Error: {str(e)}", "Evidence Validation")
        return {'error': str(e)}

@frappe.whitelist()
def extract_receipt_data_api(image_data):
    """API method for OCR receipt data extraction"""
    try:
        validator = EvidenceValidationSystem()
        
        # Decode base64 image
        image_content = base64.b64decode(image_data)
        
        # Perform OCR
        ocr_results = validator.perform_ocr_analysis(image_content, 'Expense Claim')
        
        return ocr_results
    except Exception as e:
        frappe.log_error(f"OCR Extraction Error: {str(e)}", "Evidence Validation")
        return {'error': str(e)}

@frappe.whitelist()
def analyze_image_quality(image_data):
    """API method for image quality analysis"""
    try:
        validator = EvidenceValidationSystem()
        
        # Decode base64 image
        image_content = base64.b64decode(image_data)
        
        # Analyze image
        image_analysis = validator.analyze_image_evidence(image_content)
        
        return image_analysis
    except Exception as e:
        frappe.log_error(f"Image Analysis Error: {str(e)}", "Evidence Validation")
        return {'error': str(e)} 
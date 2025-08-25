import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today
from frappe import _
import logging

# Configure logging
logger = logging.getLogger(__name__)

class Property(Document):
    """
    Enhanced Property management with categorization, mapping, and valuation tracking.
    
    Features:
    - Comprehensive property categorization
    - Geographic coordinates and mapping integration
    - Property valuation tracking
    - Accessibility and compliance tracking
    - Integration with landlord management
    """
    
    def validate(self):
        """Validate property data with enhanced checks"""
        try:
            self.validate_coordinates()
            self.validate_property_details()
            self.auto_generate_property_id()
            self.calculate_property_value()
            self.update_property_status()
        except Exception as e:
            logger.error(f"Validation error in Property {self.name}: {str(e)}")
            frappe.throw(_(f"Validation failed: {str(e)}"))
    
    def validate_coordinates(self):
        """Validate geographic coordinates"""
        if self.latitude and self.longitude:
            try:
                lat = float(self.latitude)
                lon = float(self.longitude)
                
                if not (-90 <= lat <= 90):
                    frappe.throw(_("Latitude must be between -90 and 90 degrees"))
                
                if not (-180 <= lon <= 180):
                    frappe.throw(_("Longitude must be between -180 and 180 degrees"))
                
                # Store coordinates as float for precision
                self.latitude = lat
                self.longitude = lon
                
            except ValueError:
                frappe.throw(_("Invalid coordinate format. Please enter numeric values."))
    
    def validate_property_details(self):
        """Validate property details and categorization"""
        if not self.property_name:
            frappe.throw(_("Property name is required"))
        
        if not self.full_address:
            frappe.throw(_("Full address is required"))
        
        # Validate property type categorization
        if self.property_type:
            valid_types = ["Commercial", "Residential", "Industrial", "Roadside", "Other"]
            if self.property_type not in valid_types:
                frappe.throw(_("Invalid property type"))
    
    def auto_generate_property_id(self):
        """Auto-generate property ID if not provided"""
        if not self.property_id:
            # Generate based on property type and location
            prefix = self.property_type[:3].upper() if self.property_type else "PROP"
            self.property_id = f"{prefix}-{getdate().year}-{self.name[-5:]}"
    
    def calculate_property_value(self):
        """Calculate property value based on various factors"""
        try:
            base_value = 0
            
            # Base value by property type
            type_values = {
                "Commercial": 100000,
                "Residential": 75000,
                "Industrial": 150000,
                "Roadside": 50000,
                "Other": 80000
            }
            
            base_value = type_values.get(self.property_type, 80000)
            
            # Adjust for size if available
            if hasattr(self, 'property_size') and self.property_size:
                try:
                    # Parse size (e.g., "14x48 feet")
                    size_parts = self.property_size.split('x')
                    if len(size_parts) >= 2:
                        width = float(size_parts[0])
                        length = float(size_parts[1].split()[0])
                        area = width * length
                        base_value *= (area / 1000)  # Adjust based on area
                except:
                    pass
            
            # Adjust for location (city-based)
            if self.city:
                city_multipliers = {
                    "Kampala": 1.5,
                    "Nairobi": 1.3,
                    "Dar es Salaam": 1.2,
                    "Kigali": 1.1
                }
                multiplier = city_multipliers.get(self.city, 1.0)
                base_value *= multiplier
            
            # Store calculated value
            self.calculated_value = base_value
            
            # Update market value if not manually set
            if not self.market_value:
                self.market_value = base_value
                
        except Exception as e:
            logger.error(f"Error calculating property value: {str(e)}")
    
    def update_property_status(self):
        """Update property status based on landlord occupancy"""
        try:
            # Check if property is occupied by any landlord
            occupied_count = frappe.db.count("Landlord Property", {
                "property": self.name,
                "status": "Active"
            })
            
            if occupied_count > 0:
                self.property_status = "Occupied"
            else:
                self.property_status = "Available"
                
        except Exception as e:
            logger.error(f"Error updating property status: {str(e)}")
    
    def on_update(self):
        """Actions to perform after property is updated"""
        try:
            self.update_landlord_properties()
            self.log_property_changes()
            self.update_mapping_data()
        except Exception as e:
            logger.error(f"Error in on_update for Property {self.name}: {str(e)}")
    
    def update_landlord_properties(self):
        """Update related landlord properties with new property information"""
        try:
            landlord_properties = frappe.get_all("Landlord Property", {
                "property": self.name
            })
            
            for lp in landlord_properties:
                lp_doc = frappe.get_doc("Landlord Property", lp.name)
                if self.full_address and not lp_doc.property_address:
                    lp_doc.property_address = self.full_address
                    lp_doc.save(ignore_permissions=True)
        except Exception as e:
            logger.error(f"Error updating landlord properties: {str(e)}")
    
    def log_property_changes(self):
        """Log property changes for audit trail"""
        try:
            if self.is_new():
                frappe.logger().info(f"New property created: {self.name} - {self.property_name}")
            else:
                frappe.logger().info(f"Property updated: {self.name} - {self.property_name}")
        except Exception as e:
            logger.error(f"Error logging property changes: {str(e)}")
    
    def update_mapping_data(self):
        """Update mapping data for external mapping services"""
        try:
            if self.latitude and self.longitude:
                # Store mapping data for external services
                mapping_data = {
                    "property_id": self.property_id,
                    "name": self.property_name,
                    "address": self.full_address,
                    "coordinates": {
                        "lat": self.latitude,
                        "lng": self.longitude
                    },
                    "type": self.property_type,
                    "status": self.property_status
                }
                
                # Store in custom field or separate table for mapping integration
                self.mapping_data = frappe.as_json(mapping_data)
                
        except Exception as e:
            logger.error(f"Error updating mapping data: {str(e)}")
    
    @frappe.whitelist()
    def get_property_summary(self):
        """Get comprehensive property summary for dashboard"""
        try:
            # Get landlord information
            landlords = frappe.get_all("Landlord Property", {
                "property": self.name
            }, ["parent", "status", "rental_amount"])
            
            total_rental = sum(lp.rental_amount for lp in landlords if lp.rental_amount)
            active_landlords = len([lp for lp in landlords if lp.status == "Active"])
            
            return {
                "property_id": self.property_id,
                "property_name": self.property_name,
                "property_type": self.property_type,
                "property_status": self.property_status,
                "location": {
                    "address": self.full_address,
                    "city": self.city,
                    "state": self.state_province,
                    "country": self.country,
                    "coordinates": {
                        "latitude": self.latitude,
                        "longitude": self.longitude
                    }
                },
                "valuation": {
                    "calculated_value": getattr(self, 'calculated_value', 0),
                    "market_value": getattr(self, 'market_value', 0),
                    "last_valuation_date": getattr(self, 'last_valuation_date', None)
                },
                "landlords": {
                    "total_count": len(landlords),
                    "active_count": active_landlords,
                    "total_rental": total_rental
                },
                "accessibility": {
                    "notes": self.accessibility_notes,
                    "compliance_status": getattr(self, 'compliance_status', 'Unknown')
                }
            }
        except Exception as e:
            logger.error(f"Error getting property summary: {str(e)}")
            return {}
    
    @frappe.whitelist()
    def update_valuation(self, new_value, valuation_date=None):
        """Update property valuation"""
        try:
            if not valuation_date:
                valuation_date = today()
            
            self.market_value = new_value
            self.last_valuation_date = valuation_date
            self.save(ignore_permissions=True)
            
            return {
                "success": True,
                "message": f"Property valuation updated to {new_value}"
            }
        except Exception as e:
            logger.error(f"Error updating property valuation: {str(e)}")
            return {"success": False, "message": str(e)}
    
    @frappe.whitelist()
    def get_mapping_url(self):
        """Generate mapping URL for the property"""
        try:
            if self.latitude and self.longitude:
                return f"https://www.google.com/maps?q={self.latitude},{self.longitude}"
            elif self.full_address:
                # Fallback to address-based mapping
                address = self.full_address.replace(" ", "+")
                return f"https://www.google.com/maps?q={address}"
            else:
                return None
        except Exception as e:
            logger.error(f"Error generating mapping URL: {str(e)}")
            return None 
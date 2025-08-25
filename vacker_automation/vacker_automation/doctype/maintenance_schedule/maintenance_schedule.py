import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today, add_days, add_months
from frappe import _
import logging

# Configure logging
logger = logging.getLogger(__name__)

class MaintenanceSchedule(Document):
    """
    Enhanced Maintenance Schedule with preventive maintenance and resource allocation.
    
    Features:
    - Preventive maintenance scheduling
    - Resource allocation and technician management
    - Maintenance history tracking and analytics
    - Cost tracking and budget management
    - Integration with HR module for technician management
    """
    
    def validate(self):
        """Validate maintenance schedule data with enhanced checks"""
        try:
            self.validate_scheduled_date()
            self.validate_resource_allocation()
            self.update_status()
            self.fetch_related_data()
            self.calculate_estimated_cost()
        except Exception as e:
            logger.error(f"Validation error in MaintenanceSchedule {self.name}: {str(e)}")
            frappe.throw(_(f"Validation failed: {str(e)}"))
    
    def validate_scheduled_date(self):
        """Validate scheduled date and set appropriate status"""
        if self.scheduled_date:
            scheduled_date = getdate(self.scheduled_date)
            today_date = getdate(today())
            if scheduled_date < today_date:
                if self.status == "Scheduled":
                    self.status = "Overdue"
    
    def validate_resource_allocation(self):
        """Validate resource allocation and technician assignment"""
        if hasattr(self, 'assigned_technician') and self.assigned_technician:
            # Check if technician exists and is available
            if not frappe.db.exists("Employee", self.assigned_technician):
                frappe.throw(_("Selected technician does not exist"))
            
            # Check technician availability (basic check)
            if hasattr(self, 'check_technician_availability') and self.check_technician_availability:
                if not self._is_technician_available():
                    frappe.throw(_("Selected technician is not available on scheduled date"))
    
    def _is_technician_available(self):
        """Check if assigned technician is available on scheduled date"""
        try:
            # Check for conflicting maintenance schedules
            conflicting_schedules = frappe.db.count("Maintenance Schedule", {
                "assigned_technician": self.assigned_technician,
                "scheduled_date": self.scheduled_date,
                "status": ["in", ["Scheduled", "In Progress"]],
                "name": ["!=", self.name]
            })
            
            return conflicting_schedules == 0
        except Exception as e:
            logger.error(f"Error checking technician availability: {str(e)}")
            return True  # Default to available if check fails
    
    def update_status(self):
        """Update maintenance status based on completion and scheduling"""
        if self.completed_date:
            self.status = "Completed"
        elif self.scheduled_date:
            scheduled_date = getdate(self.scheduled_date)
            today_date = getdate(today())
            if scheduled_date < today_date and self.status == "Scheduled":
                self.status = "Overdue"
    
    def fetch_related_data(self):
        """Fetch related data from media installation with enhanced logic"""
        try:
            if self.media_installation and not self.landlord:
                installation = frappe.get_doc("Media Installation", self.media_installation)
                self.landlord = installation.landlord
                self.property = installation.property
                
                # Auto-assign technician if not assigned
                if not hasattr(self, 'assigned_technician') or not self.assigned_technician:
                    self._auto_assign_technician()
        except Exception as e:
            logger.error(f"Error fetching related data: {str(e)}")
    
    def _auto_assign_technician(self):
        """Auto-assign available technician based on skills and availability"""
        try:
            # Get technicians with maintenance skills
            technicians = frappe.get_all("Employee", {
                "designation": ["like", "%Technician%"],
                "status": "Active"
            }, ["name", "employee_name"])
            
            if technicians:
                # Simple assignment - first available technician
                self.assigned_technician = technicians[0].name
                self.technician_name = technicians[0].employee_name
        except Exception as e:
            logger.error(f"Error auto-assigning technician: {str(e)}")
    
    def calculate_estimated_cost(self):
        """Calculate estimated maintenance cost based on type and resources"""
        try:
            base_costs = {
                "Routine": 100,
                "Emergency": 500,
                "Repair": 300,
                "Upgrade": 800
            }
            
            base_cost = base_costs.get(self.maintenance_type, 200)
            
            # Adjust for property type
            if self.property:
                property_doc = frappe.get_doc("Property", self.property)
                if property_doc.property_type == "Digital Display":
                    base_cost *= 1.5  # Digital displays cost more to maintain
                elif property_doc.property_type == "Billboard":
                    base_cost *= 1.2
            
            # Adjust for technician level
            if hasattr(self, 'assigned_technician') and self.assigned_technician:
                technician = frappe.get_doc("Employee", self.assigned_technician)
                if hasattr(technician, 'designation'):
                    if "Senior" in technician.designation:
                        base_cost *= 1.3
                    elif "Junior" in technician.designation:
                        base_cost *= 0.8
            
            self.estimated_cost = base_cost
            
        except Exception as e:
            logger.error(f"Error calculating estimated cost: {str(e)}")
    
    def on_update(self):
        """Actions to perform after maintenance schedule is updated with enhanced logic"""
        try:
            self.send_notifications()
            self.update_installation_status()
            self.create_maintenance_history()
            self.update_resource_calendar()
        except Exception as e:
            logger.error(f"Error in on_update for MaintenanceSchedule {self.name}: {str(e)}")
    
    def send_notifications(self):
        """Send maintenance notifications with enhanced logic"""
        try:
            if self.status == "Scheduled" and self.scheduled_date:
                days_until_maintenance = (getdate(self.scheduled_date) - getdate(today())).days
                if 0 <= days_until_maintenance <= 3:
                    self.send_maintenance_reminder(days_until_maintenance)
            elif self.status == "Completed":
                self.send_completion_notification()
            elif self.status == "Overdue":
                self.send_overdue_notification()
            elif self.status == "In Progress":
                self.send_progress_notification()
        except Exception as e:
            logger.error(f"Error sending notifications: {str(e)}")
    
    def send_maintenance_reminder(self, days_until_maintenance):
        """Send maintenance reminder with enhanced messaging"""
        try:
            landlord_email = frappe.db.get_value("Landlord", self.landlord, "email_address")
            if landlord_email:
                subject = f"Maintenance Scheduled - {days_until_maintenance} days remaining"
                
                technician_info = ""
                if hasattr(self, 'assigned_technician') and self.assigned_technician:
                    technician_info = f"\nAssigned Technician: {self.technician_name or self.assigned_technician}"
                
                message = f"""
                Dear Landlord,
                
                This is a reminder that maintenance is scheduled for your property in {days_until_maintenance} days.
                
                Property: {self.property}
                Scheduled Date: {self.scheduled_date}
                Maintenance Type: {self.maintenance_type}
                Estimated Cost: {getattr(self, 'estimated_cost', 'TBD')}{technician_info}
                
                Our technician will contact you to confirm the appointment.
                
                Best regards,
                Vacker Outdoor Advertising Team
                """
                
                frappe.sendmail(
                    recipients=[landlord_email],
                    subject=subject,
                    message=message
                )
        except Exception as e:
            logger.error(f"Error sending maintenance reminder: {str(e)}")
    
    def send_completion_notification(self):
        """Send maintenance completion notification with cost details"""
        try:
            landlord_email = frappe.db.get_value("Landlord", self.landlord, "email_address")
            if landlord_email:
                subject = f"Maintenance Completed - Property: {self.property}"
                
                cost_info = ""
                if self.maintenance_cost:
                    cost_info = f"\nActual Cost: {self.maintenance_cost}"
                elif hasattr(self, 'estimated_cost') and self.estimated_cost:
                    cost_info = f"\nEstimated Cost: {self.estimated_cost}"
                
                message = f"""
                Dear Landlord,
                
                The maintenance at your property has been completed successfully.
                
                Property: {self.property}
                Completed Date: {self.completed_date}
                Maintenance Type: {self.maintenance_type}{cost_info}
                
                Technician Notes: {self.technician_notes or 'No additional notes'}
                
                Thank you for your cooperation.
                
                Best regards,
                Vacker Outdoor Advertising Team
                """
                
                frappe.sendmail(
                    recipients=[landlord_email],
                    subject=subject,
                    message=message
                )
        except Exception as e:
            logger.error(f"Error sending completion notification: {str(e)}")
    
    def send_overdue_notification(self):
        """Send overdue maintenance notification"""
        try:
            landlord_email = frappe.db.get_value("Landlord", self.landlord, "email_address")
            if landlord_email:
                subject = f"Maintenance Overdue - Property: {self.property}"
                message = f"""
                Dear Landlord,
                
                The scheduled maintenance at your property is overdue.
                
                Property: {self.property}
                Scheduled Date: {self.scheduled_date}
                Maintenance Type: {self.maintenance_type}
                
                We will reschedule this maintenance at your earliest convenience.
                
                Best regards,
                Vacker Outdoor Advertising Team
                """
                
                frappe.sendmail(
                    recipients=[landlord_email],
                    subject=subject,
                    message=message
                )
        except Exception as e:
            logger.error(f"Error sending overdue notification: {str(e)}")
    
    def send_progress_notification(self):
        """Send maintenance progress notification"""
        try:
            landlord_email = frappe.db.get_value("Landlord", self.landlord, "email_address")
            if landlord_email:
                subject = f"Maintenance In Progress - Property: {self.property}"
                message = f"""
                Dear Landlord,
                
                Maintenance work has started at your property.
                
                Property: {self.property}
                Maintenance Type: {self.maintenance_type}
                Technician: {self.technician_name or 'Assigned'}
                
                We will notify you upon completion.
                
                Best regards,
                Vacker Outdoor Advertising Team
                """
                
                frappe.sendmail(
                    recipients=[landlord_email],
                    subject=subject,
                    message=message
                )
        except Exception as e:
            logger.error(f"Error sending progress notification: {str(e)}")
    
    def update_installation_status(self):
        """Update media installation status based on maintenance"""
        try:
            if self.media_installation:
                # Set flag to prevent circular dependency
                frappe.flags.in_maintenance_update = True
                
                try:
                    # Use direct database update to avoid triggering on_update method
                    if self.status == "In Progress":
                        frappe.db.set_value("Media Installation", self.media_installation, "installation_status", "Under Maintenance")
                    elif self.status == "Completed":
                        frappe.db.set_value("Media Installation", self.media_installation, "installation_status", "Completed")
                finally:
                    # Clear the flag
                    frappe.flags.in_maintenance_update = False
        except Exception as e:
            logger.error(f"Error updating installation status: {str(e)}")
    
    def create_maintenance_history(self):
        """Create maintenance history record for analytics"""
        try:
            if self.status == "Completed":
                # Create maintenance history record
                history = frappe.new_doc("Maintenance History")
                history.maintenance_schedule = self.name
                history.property = self.property
                history.landlord = self.landlord
                history.maintenance_type = self.maintenance_type
                history.completed_date = self.completed_date
                history.actual_cost = self.maintenance_cost
                history.estimated_cost = getattr(self, 'estimated_cost', 0)
                history.technician = getattr(self, 'assigned_technician', None)
                history.technician_notes = self.technician_notes
                history.landlord_feedback = self.landlord_feedback
                history.insert(ignore_permissions=True)
        except Exception as e:
            logger.error(f"Error creating maintenance history: {str(e)}")
    
    def update_resource_calendar(self):
        """Update resource calendar for technician allocation"""
        try:
            if hasattr(self, 'assigned_technician') and self.assigned_technician:
                # Update technician calendar (basic implementation)
                # In a full implementation, this would integrate with HR calendar system
                pass
        except Exception as e:
            logger.error(f"Error updating resource calendar: {str(e)}")
    
    @frappe.whitelist()
    def mark_as_completed(self, completed_date=None, technician_notes=None, maintenance_cost=None):
        """Mark maintenance as completed with enhanced tracking"""
        try:
            if not completed_date:
                completed_date = today()
            
            self.completed_date = completed_date
            self.status = "Completed"
            
            if technician_notes:
                self.technician_notes = technician_notes
            
            if maintenance_cost:
                self.maintenance_cost = maintenance_cost
            
            self.save(ignore_permissions=True)
            
            return {
                "success": True,
                "message": "Maintenance marked as completed successfully",
                "cost_variance": self._calculate_cost_variance()
            }
        except Exception as e:
            logger.error(f"Error marking maintenance as completed: {str(e)}")
            return {"success": False, "message": str(e)}
    
    def _calculate_cost_variance(self):
        """Calculate variance between estimated and actual cost"""
        try:
            if self.maintenance_cost and hasattr(self, 'estimated_cost') and self.estimated_cost:
                variance = self.maintenance_cost - self.estimated_cost
                variance_percentage = (variance / self.estimated_cost) * 100
                return {
                    "variance": variance,
                    "variance_percentage": variance_percentage,
                    "over_budget": variance > 0
                }
            return None
        except Exception as e:
            logger.error(f"Error calculating cost variance: {str(e)}")
            return None
    
    @frappe.whitelist()
    def reschedule_maintenance(self, new_date, reason=None):
        """Reschedule maintenance with reason tracking"""
        try:
            if not new_date:
                frappe.throw(_("New date is required"))
            
            self.scheduled_date = new_date
            self.status = "Scheduled"
            
            if reason:
                self.reschedule_reason = reason
            
            self.save(ignore_permissions=True)
            
            # Send reschedule notification
            self.send_reschedule_notification(reason)
            
            return {
                "success": True,
                "message": f"Maintenance rescheduled to {new_date}"
            }
        except Exception as e:
            logger.error(f"Error rescheduling maintenance: {str(e)}")
            return {"success": False, "message": str(e)}
    
    def send_reschedule_notification(self, reason):
        """Send reschedule notification"""
        try:
            landlord_email = frappe.db.get_value("Landlord", self.landlord, "email_address")
            if landlord_email:
                subject = f"Maintenance Rescheduled - Property: {self.property}"
                
                reason_text = f"\nReason: {reason}" if reason else ""
                
                message = f"""
                Dear Landlord,
                
                The maintenance at your property has been rescheduled.
                
                Property: {self.property}
                New Scheduled Date: {self.scheduled_date}
                Maintenance Type: {self.maintenance_type}{reason_text}
                
                We apologize for any inconvenience caused.
                
                Best regards,
                Vacker Outdoor Advertising Team
                """
                
                frappe.sendmail(
                    recipients=[landlord_email],
                    subject=subject,
                    message=message
                )
        except Exception as e:
            logger.error(f"Error sending reschedule notification: {str(e)}")
    
    @frappe.whitelist()
    def get_maintenance_summary(self):
        """Get comprehensive maintenance summary for dashboard"""
        try:
            cost_variance = self._calculate_cost_variance()
            
            return {
                "maintenance_id": self.name,
                "property": self.property,
                "landlord": self.landlord,
                "maintenance_type": self.maintenance_type,
                "scheduled_date": self.scheduled_date,
                "completed_date": self.completed_date,
                "status": self.status,
                "technician": getattr(self, 'assigned_technician', None),
                "technician_name": getattr(self, 'technician_name', None),
                "estimated_cost": getattr(self, 'estimated_cost', 0),
                "actual_cost": self.maintenance_cost,
                "cost_variance": cost_variance,
                "days_overdue": (getdate(today()) - getdate(self.scheduled_date)).days if self.scheduled_date and getdate(self.scheduled_date) < getdate(today()) else 0,
                "technician_notes": self.technician_notes,
                "landlord_feedback": self.landlord_feedback
            }
        except Exception as e:
            logger.error(f"Error getting maintenance summary: {str(e)}")
            return {}
    
    @frappe.whitelist()
    def get_maintenance_analytics(self):
        """Get maintenance analytics for reporting"""
        try:
            # Get historical maintenance data for this property
            history = frappe.get_all("Maintenance History", {
                "property": self.property
            }, ["maintenance_type", "actual_cost", "estimated_cost", "completed_date"])
            
            total_maintenance = len(history)
            total_cost = sum(h.actual_cost for h in history if h.actual_cost)
            avg_cost = total_cost / total_maintenance if total_maintenance > 0 else 0
            
            # Calculate cost efficiency
            cost_efficiency = 0
            if history:
                estimated_total = sum(h.estimated_cost for h in history if h.estimated_cost)
                if estimated_total > 0:
                    cost_efficiency = ((estimated_total - total_cost) / estimated_total) * 100
            
            return {
                "total_maintenance_count": total_maintenance,
                "total_cost": total_cost,
                "average_cost": avg_cost,
                "cost_efficiency_percentage": cost_efficiency,
                "maintenance_frequency": self._calculate_maintenance_frequency(history)
            }
        except Exception as e:
            logger.error(f"Error getting maintenance analytics: {str(e)}")
            return {}
    
    def _calculate_maintenance_frequency(self, history):
        """Calculate maintenance frequency based on history"""
        try:
            if len(history) < 2:
                return "Insufficient data"
            
            # Calculate average days between maintenance
            dates = sorted([h.completed_date for h in history if h.completed_date])
            if len(dates) >= 2:
                total_days = 0
                for i in range(1, len(dates)):
                    total_days += (getdate(dates[i]) - getdate(dates[i-1])).days
                
                avg_days = total_days / (len(dates) - 1)
                return f"{avg_days:.0f} days"
            
            return "Insufficient data"
        except Exception as e:
            logger.error(f"Error calculating maintenance frequency: {str(e)}")
            return "Error" 
# Multi-Property Landlord Management System

## Overview

The Landlord Management System has been enhanced to support **one landlord managing multiple properties**. This is a common scenario in outdoor advertising where a single landlord or company owns multiple billboard locations, digital displays, or other advertising spaces.

## Key Changes

### 1. **Landlord DocType Structure**

**Before (One-to-One):**
```
Landlord → Property
```

**After (One-to-Many):**
```
Landlord → Multiple Properties (Child Table)
```

### 2. **New Child Table: Landlord Property**

A new child table `Landlord Property` has been created to store individual property details for each landlord:

#### Fields in Landlord Property:
- **Property** (Link to Property DocType)
- **Property Address** (Auto-fetched from Property)
- **Media Type** (Billboard, Digital Display, etc.)
- **Contract Start Date**
- **Contract End Date**
- **Lease Agreement Number**
- **Rental Amount** (per property)
- **Payment Frequency** (per property)
- **Status** (Active, Inactive, Expired, Terminated)

### 3. **Updated Landlord Fields**

#### Removed Fields:
- `property` (single property link)
- `property_address`
- `media_type`
- `contract_start_date`
- `contract_end_date`
- `lease_agreement_number`

#### Added Fields:
- `properties` (child table)
- `rental_amount` (now calculated as total from all properties)

## Benefits of Multi-Property System

### 1. **Realistic Business Model**
- One landlord can manage multiple advertising locations
- Different rental amounts per property
- Different contract terms per property
- Different payment frequencies per property

### 2. **Better Financial Management**
- Total rental amount automatically calculated
- Individual property tracking
- Property-specific payment schedules
- Commission calculations per property

### 3. **Enhanced Reporting**
- Property-wise revenue analysis
- Landlord portfolio overview
- Contract expiry tracking per property
- Performance metrics per location

## How to Use

### 1. **Creating a New Landlord**

1. Go to **Landlord** → **New**
2. Fill in basic landlord information:
   - Landlord ID
   - Full Legal Name
   - Contact Information
   - Payment & Banking Details

3. **Add Properties:**
   - Click **"Add Property"** button
   - Select property from dropdown
   - Enter contract details
   - Set rental amount and payment frequency
   - Save

4. **Add More Properties:**
   - Repeat the process for additional properties
   - Total rental amount updates automatically

### 2. **Managing Properties**

#### Adding Properties:
- Use the **"Add Property"** button
- Fill in property-specific details
- Contract dates are validated
- Property address auto-fetches from Property DocType

#### Editing Properties:
- Click on any property row in the child table
- Modify details as needed
- Total rental amount recalculates automatically

#### Removing Properties:
- Delete property rows from the child table
- Total rental amount updates accordingly

### 3. **Payment Schedules**

- **Generate Payment Schedules** button creates schedules for all active properties
- Each property can have different payment frequencies
- Payment schedules are created per property
- Overdue tracking per property

## Business Logic

### 1. **Total Rental Calculation**
```python
def calculate_total_rental_amount(self):
    total_amount = 0
    if self.properties:
        for property_item in self.properties:
            if property_item.rental_amount and property_item.status == "Active":
                total_amount += property_item.rental_amount
    self.rental_amount = total_amount
```

### 2. **Annual Revenue Calculation**
```python
def calculate_annual_revenue(self):
    total_annual_revenue = 0
    if self.properties:
        for property_item in self.properties:
            if property_item.rental_amount and property_item.status == "Active":
                if property_item.payment_frequency == "Monthly":
                    total_annual_revenue += property_item.rental_amount * 12
                elif property_item.payment_frequency == "Quarterly":
                    total_annual_revenue += property_item.rental_amount * 4
                elif property_item.payment_frequency == "Annually":
                    total_annual_revenue += property_item.rental_amount
    return total_annual_revenue
```

### 3. **Contract Expiry Notifications**
- System tracks expiry dates for each property
- Sends notifications 90 days before expiry
- Property-specific reminder emails

## Dashboard Integration

### 1. **Landlord Summary**
- Total properties count
- Active properties count
- Total rental amount
- Property-wise breakdown

### 2. **Revenue Analysis**
- Revenue by landlord type
- Revenue by media type
- Property status distribution
- Contract expiry tracking

## Validation Rules

### 1. **Landlord Level**
- At least one property required
- Contact information validation
- Payment method validation

### 2. **Property Level**
- Contract end date must be after start date
- Rental amount must be positive
- Property must be selected
- Contract dates cannot be in the past

## Migration Notes

### 1. **Existing Data**
- Existing landlords with single properties need to be updated
- Property information moved to child table
- Payment schedules need regeneration

### 2. **Data Migration Script**
```python
# Example migration script for existing landlords
def migrate_single_property_landlords():
    landlords = frappe.get_all("Landlord", filters={"property": ["!=", ""]})
    
    for landlord_name in landlords:
        landlord = frappe.get_doc("Landlord", landlord_name.name)
        
        # Create child table entry
        child = landlord.append("properties")
        child.property = landlord.property
        child.property_address = landlord.property_address
        child.media_type = landlord.media_type
        child.contract_start_date = landlord.contract_start_date
        child.contract_end_date = landlord.contract_end_date
        child.lease_agreement_number = landlord.lease_agreement_number
        child.rental_amount = landlord.rental_amount
        child.payment_frequency = landlord.payment_frequency
        child.status = "Active"
        
        landlord.save()
```

## Best Practices

### 1. **Property Management**
- Use descriptive property names
- Keep contract dates accurate
- Update property status regularly
- Monitor contract expiries

### 2. **Financial Tracking**
- Review total rental amounts regularly
- Monitor payment schedules
- Track commission calculations
- Generate regular reports

### 3. **Communication**
- Send welcome emails for new landlords
- Monitor contract expiry notifications
- Keep landlord information updated
- Maintain property documentation

## Future Enhancements

### 1. **Advanced Features**
- Property portfolio analytics
- Revenue forecasting
- Contract renewal automation
- Performance benchmarking

### 2. **Integration**
- Accounting system integration
- CRM integration
- Mobile app support
- API endpoints

### 3. **Reporting**
- Custom dashboard widgets
- Advanced filtering options
- Export capabilities
- Scheduled reports

---

## Conclusion

The multi-property landlord system provides a more realistic and flexible approach to managing outdoor advertising relationships. It supports complex business scenarios where landlords manage multiple properties with different terms, amounts, and payment schedules.

This enhancement makes the system more scalable and better suited for real-world outdoor advertising operations. 
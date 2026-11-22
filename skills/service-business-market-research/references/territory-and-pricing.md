# Territory and pricing decision recipe

Use when a service radius, route day or distant appointment changes the economics. Do not retain a particular project's prices, coordinates or labor assumptions as defaults.

## 1. Identify the actual journey

Collect an origin ZIP/public intersection, likely departure and return windows, actual customer destination if available, number of traveling technicians and intended service duration. Keep public-landmark or town-center routes explicitly provisional.

Use the loaded maps skill's geocoding and route workflow. Validate the matched settlement, county and feature type before accepting a route. A successful geocoder can return an unrelated parcel or county. Cache verified coordinates so a transport retry does not repeat discovery.

Preserve route duration, distance, origin/destination labels, source endpoint and retrieval time. Label baseline road-model estimates separately from live traffic. Check outbound and return feasibility before advertising a firm drive-time boundary.

## 2. Seek both an opportunity and its counterexample

| Evidence | Permitted interpretation | Unsupported shortcut |
|---|---|---|
| Chamber/business support page | A way to conduct discovery | Members are qualified network-service leads |
| Development/property changes | A possible job trigger | A verified project pipeline or eligible subsidy |
| Supplier city landing page | Advertised service coverage | A staffed town office |
| Regional dispatch without storefront | A valid delivery model to compare | The town lacks service |
| Published travel/scheduling terms | A concrete offer attribute to test | Provider refuses work or our delivery is cheaper |
| Missing page, price or address | An unresolved question | Concealment, unavailable service or an empty market |

Search alternative suppliers beyond the initial competitors. Retain generic providers and customer-managed/ISP alternatives when they could solve the actual problem. Rank a scheduling or job-fit hypothesis, not a town-wide absence claim.

## 3. Specify the job before selecting a price

Write the deliverable and acceptance tests, onsite and total-person-hour caps, authorized devices/systems, included visits, travel treatment, hardware/tax handling, diagnostic-credit rule and stop/requote condition.

Separate free qualification from paid diagnosis and from implementation. State whether the customer pays for findings even if repair is declined or infeasible. Do not imply a fix is guaranteed by the diagnostic price.

## 4. Calculate an explicit economic model

Use `execute_code` or `terminal`; retain inputs and results in JSON or CSV. Include sales, intake, preparation, travel, onsite work, documentation, partner coordination and follow-up. Count every technician's time even when traveling in one vehicle.

Use variables rather than hard-coded project defaults:

```text
person_hours = sum(each person's nontravel hours + travel hours)
vehicle_cost = driven_miles * assumed_vehicle_cost_per_mile
modeled_cost = person_hours * labor_value_per_hour + vehicle_cost + allocated_overhead + other_job_costs
candidate_price = modeled_cost / (1 - target_contribution_fraction)
residual_at_test_price = test_price - modeled_cost
```

Explain that the divisor targets a share of revenue after stated costs; it is not a markup on cost. Keep labor opportunity value separate from wages owed or cash paid. Label vehicle allowances as assumptions unless a particular official mileage rule has been independently sourced and is applicable. Contribution is not net profit or take-home pay.

Apply diagnostic credits to combined collected revenue. Do not count an assessment both as separate revenue and as fully credited implementation revenue.

## 5. Stress-test the travel policy

Recalculate for an attributable callback, extra technician, longer appointment, traffic delay and unsuccessful diagnosis. Make the callback example include repeat travel, not only onsite minutes.

A drive-time ceiling is not an included-travel zone. Test a disclosed trip component, a higher scoped total or genuinely grouped route-day appointments. Do not create a route-day forecast from assumed booking density. Do not promise emergency support to make a distant visit appear attractive.

Distinguish workmanship correction from new ISP/application/device faults in the agreement. Do not retroactively label a provider-caused defect as chargeable new travel.

## 6. Compare real purchasing decisions

Show a complete price and comparable scope, not merely an hourly rate. When competitor rates are unpublished, say there is no defensible numeric benchmark from the reviewed evidence.

Test candidate packages sequentially with consistent, explainable terms. Record booked/declined outcomes and the stated reason. A request for free advice, a favorable comment or a discounted pilot does not prove normal-price demand.

Continue only when real bookings support the itinerary, job economics and promised aftercare. Keep a closer comparison market so distance itself is not mistaken for an advantage. Confirm the actual origin before finalizing territory or trip pricing.

# GridScript™ Language Specification

GridScript™ is a lightweight, fictional formula language designed for multidimensional data modeling and grid-based computation. It resembles typical enterprise modeling languages but is intentionally generic and vendor-neutral.

> **Important:** This draft reflects only the features implemented so far in the prototype model. **Only two functions are currently supported:** `FLOWROLL()` and `DIMMATCH()`. All other language constructs are placeholders.

---

## 1. Overview

GridScript™ is a cell-oriented, declarative expression language used to derive values from:

* Lists and hierarchies
* Line items
* Time periods
* Multidimensional structures
* Mapping relationships between dimensions

Expressions operate over *grids*—structured combinations of dimensions that determine the shape of calculated data.

---

## 2. Syntax Basics

### 2.1 Identifiers

```
LineItemName
List.Member
Hierarchy.Parent.Child
```

Identifiers refer to values in a dimensional grid.

### 2.2 Literals

```
123
"BACKWARD"
"FORWARD"
```

GridScript™ supports numeric and string literals.

### 2.3 Operators

Operators are minimal for now:

```
+
-
*
/
```

Used only inside function arguments.

---

## 3. Implemented Functions

The prototype training includes only **two** GridScript™ functions. All other functions are intentionally undefined.

---

# 3.1 `FLOWROLL()`

Rolling aggregation over sequential time periods.

### **Signature**

```
FLOWROLL(LineItem, PeriodCount, Direction)
```

### **Arguments**

| Parameter     | Type    | Description                                |
| ------------- | ------- | ------------------------------------------ |
| `LineItem`    | Numeric | Source values to roll over                 |
| `PeriodCount` | Integer | Number of periods to include (must be > 0) |
| `Direction`   | Text    | "BACKWARD" or "FORWARD"                    |

### **Behavior**

* Computes a **directional rolling sum**.
* Windows extending beyond available periods return **blank**.
* Negative `PeriodCount` values cause compile-time failure.
* Only works on **sequential time dimensions**.
* Does **not** forecast, impute, or interpolate missing data.

### **Examples**

```
FLOWROLL(Sales, 3, "BACKWARD")
```

Returns the sum of the current period + previous 2 periods.

```
FLOWROLL(Inventory, 2, "FORWARD")
```

Returns the current period + next period.

---

# 3.2 `DIMMATCH()`

Structural alignment between two dimensional lists.

### **Signature**

```
DIMMATCH(SourceValue, SourceDim, TargetDim)
```

### **Arguments**

| Parameter     | Type | Description              |
| ------------- | ---- | ------------------------ |
| `SourceValue` | Any  | Value to broadcast/align |
| `SourceDim`   | List | Originating dimension    |
| `TargetDim`   | List | Destination dimension    |

### **Behavior**

* Aligns values across **structurally compatible** lists.
* Uses the underlying mapping relationships between `SourceDim` and `TargetDim`.
* If no mapping exists → result is **blank**.
* Empty target dimension → blank.
* Does **not** perform validation or quality checks.
* Single-value line items are **broadcast** across `TargetDim`.
* Time cannot be used as a target dimension.

### **Examples**

```
DIMMATCH(UnitPrice, Products, Channels)
```

Broadcasts unit prices to each channel *if* a mapping exists.

```
DIMMATCH(Total, Regions, Regions)
```

Identity alignment.

---

## 4. Unimplemented / Placeholder Areas

These features exist conceptually but are **not implemented in the prototype model and the model does not know about them**:

### ✗ Math functions

`SUM`, `AVERAGE`, `MIN`, `MAX`, etc.

### ✗ Logical functions

`IF`, `AND`, `OR`, `NOT`.

### ✗ Time intelligence

`PERIODOFFSET`, `MOVINGAVERAGE`, `CUMULATE`.

### ✗ Hierarchy navigation

`PARENT()`, `CHILDREN()`, etc.

### ✗ Dimensional aggregations

`SUM over list`, `LOOKUP`, `SELECT` equivalents.

These are intentionally excluded to demonstrate how the model behaves when only a **very limited DSL** is provided.

---

## 5. Notes for End Users

* This specification describes **fictional behavior** for hackathon/demo purposes.
* Only `FLOWROLL` and `DIMMATCH` are supported at this stage.
* The model was trained **exclusively** on examples involving these two functions.
* Any other function use will result in fallback behavior or hallucination.

---

## 6. Version

**GridScript™ Draft v0.1** — Limited function implementation (FLOWROLL + DIMMATCH only).

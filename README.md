# Tubes-IF3140
## Introduction
This repository contains Python implementations of three prominent Database Concurrency Control algorithms: Two-Phase Locking (2PL), Optimistic Concurrency Control (OCC), and Multi-Version Concurrency Control (MVCC). These algorithms play a crucial role in managing the concurrent access of transactions to a database to ensure consistency and isolation.

## Algorithms

### 1. Two-Phase Locking (2PL)

The Two-Phase Locking algorithm is a classic concurrency control protocol that uses locks to enforce consistency during the execution of transactions.

### 2. Optimistic Concurrency Control (OCC)

Optimistic Concurrency Control (OCC) is a concurrency control strategy employed in database management systems to facilitate concurrent access by multiple transactions. Unlike traditional locking mechanisms, OCC allows transactions to proceed without acquiring locks during their execution phase.

### 3. Multi-Version Concurrency Control (MVCC)

Multi-Version Concurrency Control (MVCC) is a sophisticated concurrency control mechanism widely employed in database management systems, offering a balance between high concurrency and data consistency. MVCC enables multiple versions of a database record to coexist concurrently, each associated with a specific transaction timestamp.

## Development

1. Clone the github repository https://github.com/Enliven26/Tubes-IF3140.  
2. Move to the repository folder 
```bash
cd local/path/to/Tubes-IF3140
```
3. Move to src folder to run the program.  
```bash
cd src
python main.py
```
atau  
```bash
cd src
python test.py
```

## Usage  
### Format input file
#### Read Instruction
R [TRANSACTION ID] [RESOURCE ID]
#### WRITE INSTRUCTION
W [TRANSACTION ID] [RESOURCE ID]=[INTEGER UPDATE VALUE]
#### COMMIT INSTRUCTION
C [TRANSACTION ID]

### Run Program
```bash
cd src
python main.py
```

Note:  
1. File name is the file with location relative to the src/input folder.
2. Extension in file name input is not required and all extension other than .txt will be overridden.  
3. Program will output transaction processes in the console.  
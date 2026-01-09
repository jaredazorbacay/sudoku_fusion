#pragma once
#include "board.h"

class SudokuSA
{
	Board sol;	// current working solution
    Board bestSol;
    Board currentSol;
    int bestCost;
    double coolingRate;
    double stoppingTemp;
    double initialTemp;
    double acceptanceProbability;

public:	
	SudokuSA(Board sol, double coolingRate, double stoppingTemp, double InitialTemp): sol(sol), coolingRate(coolingRate), stoppingTemp(stoppingTemp),  initialTemp(InitialTemp) {}
    int Anneal();
    int ComputeCost();
    void FillEmptyCells();
    Board GetSolution(){return sol;}
private:
    int TryRandomSwap(int oldCost);
    void CleanDuplicates();
    int LocalConflicts(int idx);
    
}; 

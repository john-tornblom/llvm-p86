PROGRAM NewtonTest;

VAR
   i : LONGINT;
   r : REAL;
   
FUNCTION Newton(Number: REAL) : REAL;
(* Find square root using Newton's method *)
VAR
   NewGuess, Delta, Epsilon, Sqrt : REAL;
BEGIN			    
   Epsilon := 0.001;
   NewGuess := (Number / 2.0) + 1.0;
   Sqrt := 0.0;
   Delta := NewGuess - Sqrt;
   WHILE Delta > Epsilon DO
   BEGIN
      Sqrt := NewGuess;
      NewGuess := (Sqrt + (Number / Sqrt)) / 2.0;
      Delta := NewGuess - Sqrt;
      IF Delta < 0.0 THEN
	 Delta := -Delta;
   END; (* END WHILE *)
   Newton := Sqrt;
END;

BEGIN
   r := 0;
   FOR i := 1 TO 10000000 DO
   BEGIN
      r := r + Newton(i);
   END;
   
   WriteLn(r);
END.
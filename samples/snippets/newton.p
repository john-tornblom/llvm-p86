PROGRAM NewtonTest;

VAR
   r : REAL;
   
PROCEDURE Newton(Number: REAL; VAR Sqrt : REAL);
(* Find square root using Newton's method *)
VAR
   NewGuess, Delta, Epsilon : REAL;
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
END;

BEGIN
   Newton(64, r);
   Writeln(r);
END.
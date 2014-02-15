PROGRAM Test;
VAR
   radius : REAL;
	  
FUNCTION CircleArea(r : REAL): REAL;
BEGIN
   CircleArea := 3.1415 * r * r;
END;

BEGIN
   WRITE('Area of circle with radius 2.0: ');
   WRITELN(CircleArea(2.0):6:1);
   WRITE('Area of circle with radius 5.0: ');
   WRITELN(CircleArea(5.0):6:1);
   WRITE('Enter your own radius: ');
   READLN(radius);
   WRITE('Area of circle with radius ', radius:3:1,': ');
   WRITELN(CircleArea(radius));   { ugly - formatting missing for real }
   radius := 5.0;
   radius := CircleArea(radius);
   WRITELN(radius);               { can you guess the output ? }
END.
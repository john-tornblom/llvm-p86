Module Triangle;

$include (triangle.i86)

Private Triangle;

   Procedure SetTriangleSides(var t : T_TRIANGLE; s1, s2, s3: longint);
   begin
      t.s1 := s1;
      t.s2 := s2;
      t.s3 := s3;
   end; { SetTriangleSides }

   Function TrianglePerimeter(s1, s2, s3: longint) : longint;
   begin
      if (s1 <= 0) or (s2 <= 0) or (s3 <= 0) then
	 TrianglePerimeter := -1
      else
	 TrianglePerimeter := (s1 + s2 + s3);
   end; { TrianglePerimeter }

   Function TriangleArea(s1, s2, s3: longint) : real;
   Var
      p	: longint;
      k	: longreal;
   begin
      p := TrianglePerimeter(s1, s2, s3);
      if (p <= 0) then
	 TriangleArea := -1
      else
      begin
	 k := p / 2;
	 TriangleArea := Sqrt(k * (k - s1) * (k - s2) * (k - s3));
      end;
   end;

   Function TriangleType(s1, s2, s3: longint) : T_TYPE;
   var
      t	: integer;

   begin
      TriangleType := ERR;
      
      t := 0;
      if s1 = s2 then
	 t := t + 1;
      
      if s1 = s3 then
	 t := t + 2;
      
      if s2 = s3 then
	 t := t + 3;
      
      if t = 0 then
      begin
	 if (s1 + s2 <= s3) or (s2 + s3 <= s1) or (s1 + s3 <= s2) then
	    TriangleType := ERR
	 else
	    TriangleType := SCA;
      end
      else if t > 3 then
	 TriangleType := EQU   
      else if (t = 1) and (s1 + s2 > s3) then
	 TriangleType := ISO
      else if (t = 2) and (s1 + s3 > s2) then
	 TriangleType := ISO
      else if (t = 3) and (s2 + s3 > s1) then
	 TriangleType := ISO
      else
	 TriangleType := ERR;
      
      if (s1 <= 0) or (s2 <= 0) or (s3 <= 0) then
	 TriangleType := ERR;
      
   end; { TriangleType }

. { Module Triangle }

{ Local Variables: }
{ mode: pascal }
{ End: }

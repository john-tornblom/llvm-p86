program matrix;

const
   size	= 199;

type
   tMatrix = array[0..size, 0..size] of longint;

var
   NUM, I     : longint;
   M1, M2, MM : tMatrix;

procedure mkmatrix(rows, cols : longint; var mx : tMatrix);
var 
   R, C, count : longint;
begin	       
   rows := rows - 1;
   cols := cols - 1;

   count := 1;
   for R := 0 to rows do
   begin
      for C := 0 to cols do
      begin
	 mx[R, C] := count;
	 count := count + 1;
      end;
   end;
End;

procedure mmult(rows, cols : longint; var m1, m2, mm : tMatrix );
var
    i, j, k, val: longint;
begin
   rows := rows - 1;
   cols := cols - 1;

    For i := 0 To rows do
    begin
        For j := 0 To cols do
        begin
            val := 0;
            For k := 0 To cols do
            begin
	       val := val + (m1[i, k] * m2[k, j]);
            end;
            mm[i, j] := val;
        end;
    end;
End;


begin
   NUM := 1000;

   mkmatrix(size, size, M1);
   mkmatrix(size, size, M2);
    
   for I := 0 To NUM do
   begin
      mmult(size, size, M1, M2, MM);
   end;

   WriteLn(MM[0, 0], '  ', MM[2, 3], '  ', MM[3, 2], '  ', MM[4, 4]);
end.

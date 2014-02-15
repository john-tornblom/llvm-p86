program vectorsum;

const
   SIZE	= 10000;

type
   VECTOR_T = array[1..SIZE] of longint;
   
var
   v : VECTOR_T;
   s : longint;
   i : longint;
   
procedure mkVector(var vec: VECTOR_T);
var 
   i : longint;
begin	       
   for i := 1 to SIZE do
   begin
      vec[i] := i;
   end;
end; { mkVector }

function sumVector(var vec : VECTOR_T) : longint;
var 
   i   : longint;
   sum : longint;
begin
   sum := 0;
   for i := 1 to SIZE do
   begin
      sum := sum + vec[i];
   end;

   sumVector := sum;
end; { sumVector }

begin
   WriteLn('N = ', SIZE);

   for i := 1 To SIZE do
   begin
      mkVector(v);
      s := sumVector(v);
   end;

   WriteLn('Sum = ', s);
end.

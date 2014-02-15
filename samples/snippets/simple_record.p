Program SimpleRecordTest;

Type
   T_DATE = Record
	       day   : Integer;
	       month : Integer;
	       year  : Integer;
	    end;     
	     
Var
   date	: T_DATE;
   i	: Integer;
   
Procedure Copy(Var ref: Integer; value : Integer);
Begin
   ref := value;
End; { Copy }


Procedure Assert(value, expected : Integer);
Begin
   If value = expected Then
      Writeln('OK')
   Else
      Halt(1);
End; { Assert }

Begin
   date.day := 3;
   date.month := 1;
   date.year := 1984;

   Assert(date.day, 3);
   Assert(date.month, 1);
   Assert(date.year, 1984);
End.
Program WeekProgram;
Type
   DAY_T = (MON, TUE, WED, THU, FRI, SAT, SUN);

Function IsWeekend(day : DAY_T) : Boolean;
Begin
   If (day = SAT) or (day = SUN) Then
      IsWeekend := True
   Else
      IsWeekend := False;
End; { IsWeekend }


Function IsWeekend2(d1, d2 : DAY_T) : Boolean;
Begin
   If (d1 = SAT) and (d2 = SUN) Then
      IsWeekend2 := True
   Else If (d2 = SAT) and (d1 = SUN) Then
      IsWeekend2 := True
   Else
      IsWeekend2 := False;   
End; { IsWeekend2 }


Begin
   If (GetMutationCount > 0) and (ParamCount > 0) Then
       SetMutation(ord(ParamStr(1)));

   WriteLn('Mon ', IsWeekend(MON));
   WriteLn('Tue ', IsWeekend(TUE));
   WriteLn('Wed ', IsWeekend(WED));
   WriteLn('Thu ', IsWeekend(THU));
   WriteLn('Fri ', IsWeekend(FRI));
   WriteLn('Sat ', IsWeekend(SAT));
   WriteLn('Sun ', IsWeekend(SUN));

   WriteLn('Mon Tue ', IsWeekend2(MON, TUE));
   WriteLn('Sat Mon ', IsWeekend2(SAT, MON));
   WriteLn('Mon Sat ', IsWeekend2(MON, SAT));
   WriteLn('Sun Mon ', IsWeekend2(SUN, MON));
   WriteLn('Mon Sun ', IsWeekend2(MON, SUN));
  
   WriteLn('Sat Sun ', IsWeekend2(SAT, SUN));
   WriteLn('Sun Sat ', IsWeekend2(SUN, SAT));
End.

import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-home',
  imports: [RouterModule],
  templateUrl: './home.html',
  styleUrl: './home.css',
})
export class Home {
    totalFilings: number = 0;
    pendingFilings: number = 0;
    approvedFilings: number = 0;
    objections: number = 0;
    advocateName: string = 'Sagar Pradhan';
    ngOnInit(): void{
      this.getFilingNumbers();
    }
    ngAfterViewInit(): void{
      let allValues = document.querySelectorAll('.value');
      allValues.forEach((singleValue:any) => {
        let startValue = 0
        let endValue = parseInt(singleValue.getAttribute("data-value"));
        if(endValue !== 0){
          let duration = Math.floor(1000 / endValue);
          let counter = setInterval(() => {
            startValue += 1;
            singleValue.textContent = startValue;
            if(startValue === endValue){
              clearInterval(counter);
            }
          }, duration) 
        }
      })
    }
    getFilingNumbers(){
      this.totalFilings = 148;
      this.pendingFilings = 32;
      this.approvedFilings = 96;
      this.objections = 20;
    }
}

const checkThatNavBarExists = ( ) =>{
    cy.get('nav').contains(/api docs/i).parent().parent().within(() => {
      cy.contains(/api docs/i)
      cy.contains(/examples/i)
      cy.contains(/blog/i)
      cy.contains(/user manual/i)
    })
  }
  

  
  describe('E2E Tests', () => {
    it('can view / (landing page)', () => {
      cy.visit('http://localhost:3000')
      checkThatNavBarExists()
      cy.contains(/The Universal Quantum Toolkit/i)
      cy.contains(/pip install pytket/i)
      cy.contains(/build/i)
      cy.contains(/compile/i)
      cy.contains(/run/i)
      
    })
  
    
  })

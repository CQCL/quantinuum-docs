const checkThatNavBarExists = () => {
    cy.get('nav').contains(/λambeq/i).parent().parent().within(() => {
      cy.contains(/λambeq/i)
    })
  }
  
  describe('E2E Tests', () => {
    it('can view / (landing page)', () => {
      cy.visit('http://localhost:3000/lambeq/')
      checkThatNavBarExists()
      cy.contains(/natural language processing on quantum computers/i)
      cy.contains(/pip install lambeq/i)
      cy.contains(/github/i)
      cy.contains(/discord/i)
      cy.contains(/getting started/i)
      cy.contains(/tutorials/i)
      cy.contains(/advanced/i)
    })
  
    it("examples is accessed from Navbar -> Lambeq", () => {  
      cy.visit('http://localhost:3000/lambeq/')
      cy.contains('button', 'λambeq').should('be.visible')
      cy.contains('button', 'λambeq', { timeout: 15000 }).click();
      cy.contains(/a python toolkit for quantum natural language processing/i).should("be.visible")
      cy.contains(/getting started/i).should("be.visible")
      cy.contains(/user guide/i).should("be.visible")
      cy.contains(/tutorials/i).should("be.visible")
      cy.contains(/code examples/i).should("be.visible")
      cy.contains(/api reference/i).click();
      cy.contains(/lambeq package/i)
    })
  
    it('inspect getting started', () => {
      cy.visit('http://localhost:3000//lambeq/intro.html')
      checkThatNavBarExists()
      cy.contains(/what is lambeq?/i)
    })
  
    it('inspect user guide', () => {
      cy.visit('http://localhost:3000/lambeq/pipeline.html')
      checkThatNavBarExists()
      cy.contains(/pipeline/i)
      cy.contains(/syntax tree for the sentence is obtained/i)
    })

    it('inspect tutorials', () => {
        cy.visit('http://localhost:3000/lambeq/tutorials/sentence-input.html')
        checkThatNavBarExists()
        cy.contains(/step 1. sentence input/i)
        cy.contains(/pre-processing and tokenisation/i)
        cy.contains(/syntax-based model: discocat/i)
    })

    it('inspect examples', () => {
        cy.visit('http:localhost:3000/lambeq/notebooks.html')
        checkThatNavBarExists()
        cy.contains(/tokenisation/i)
    })
  
   it.skip('can link to root docs page from lambeq guides page', () => {
      cy.visit('http://localhost:3000/lambeq/guides.html')
     cy.findByLabelText(/quantinuum documentation/i).click()
    cy.origin('https://docs.quantinuum.com', () => {
    cy.contains(/technical documentation/i)
   })
  })
  })
  
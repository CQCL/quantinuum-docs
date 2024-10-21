export const checkThatNavBarExists = () => {
cy.get('nav').contains(/nexus/i).parent().parent().within(() => {
    cy.contains(/nexus/i)
})
}